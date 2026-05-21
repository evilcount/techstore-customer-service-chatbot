# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jupyter notebook-based customer service chatbot for **TechStore Plus** (fictional e-commerce tech store). The project spans multiple weeks:

- **Week 1** — `TechStorePlus_Customer_Service_Chatbot_Project.ipynb`: OpenAI API called directly, manual JSON parsing, rule-based mock mode.
- **Week 2** — `TechStorePlus_LangChain_LCEL_Chatbot.ipynb`: Refactored with LangChain LCEL, Pydantic structured output, LangSmith tracing.

## Environment Setup

The project uses a local `.venv` virtual environment.

```powershell
# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1

# Install dependencies (if starting fresh)
pip install -r requirements.txt
```

API keys are loaded from `.env`:
```
OPENAI_API_KEY=<your-key>
LANGCHAIN_API_KEY=<your-langsmith-key>   # optional, enables LangSmith tracing
```

## Running the Notebooks

**Week 1:**
```powershell
jupyter notebook TechStorePlus_Customer_Service_Chatbot_Project.ipynb
```
Run cells top-to-bottom. The **Mock Mode cell** (section 9) overrides the OpenAI functions with local rule-based equivalents — set `MOCK_MODE = True` to run without consuming API credits.

**Week 2:**
```powershell
jupyter notebook TechStorePlus_LangChain_LCEL_Chatbot.ipynb
```
Run cells top-to-bottom. LangSmith tracing is optional — the chain runs normally without `LANGCHAIN_API_KEY`. The env vars `LANGCHAIN_TRACING_V2` and `LANGCHAIN_PROJECT` must be set **before** any `ChatOpenAI` is instantiated (cell 1 handles this).

## Architecture

### Week 1 — Core Data Flow

```
user query
  → analyze_customer_query()          # gpt-4o-mini, temp=0 → structured JSON dict
  → generate_personalized_response()  # gpt-4o-mini, temp=0.4 → reply string
  → chatbot_reply()                   # orchestrates above two, returns combined dict
  → generate_conversation_summary()   # gpt-4o-mini, temp=0.2 → JSON summary dict
  → save_conversation_json()          # writes to conversation_data/<customer_id>_<timestamp>.json
  → consolidate_conversations()       # merges all files into consolidated_conversations.json
```

### Week 1 — Key Classes and Functions

- `ConversationSession` — holds per-session message history (including system role); exposes `add_user_message`, `add_assistant_message`, `get_public_history`.
- `chatbot_reply(session, query)` — single entry point for processing a customer message.
- `COMPANY_CONTEXT` dict — the knowledge base injected into `SYSTEM_ROLE`. Edit here to change company info.
- `SYSTEM_ROLE` — f-string system prompt defining behavior and conversation flow.

### Week 1 — Execution Modes

- **OpenAI mode** (default): `analyze_customer_query`, `generate_personalized_response`, and `generate_conversation_summary` all call `gpt-4o-mini`.
- **Mock mode** (`MOCK_MODE = True`): the same three functions are overridden in-cell with pure-Python keyword/regex implementations. No API calls are made.

### Week 2 — LCEL Chain

```
Input: {"query": str, "customer_id": str}
  ↓
RunnablePassthrough.assign(analysis=lambda | analysis_chain)
  → analysis_prompt | llm.with_structured_output(QueryAnalysis)   [temp=0]
  ↓
RunnablePassthrough.assign(response=RunnableLambda(route_response))
  → CATEGORY_PROMPTS[category] | response_llm                     [temp=0.4]
  ↓
RunnableLambda(build_summary)
  → deterministic assembly → ConversationSummary (Pydantic)
```

### Week 2 — Key Components

- `QueryAnalysis` — Pydantic model with typed `Literal` fields; validated via `with_structured_output()`.
- `analysis_chain` — `analysis_prompt | llm.with_structured_output(QueryAnalysis)`.
- `CATEGORY_PROMPTS` — dict of 5 `ChatPromptTemplate` (one per category); each defines a specialist persona.
- `route_response(inputs)` — `RunnableLambda` that dispatches to the correct category prompt at runtime.
- `ConversationSummary` — Pydantic model matching the Week 1 JSON structure.
- `build_summary(inputs)` — assembles `ConversationSummary` programmatically from analysis (no extra LLM call).

### Conversation Persistence (both weeks)

- Each conversation saves to `conversation_data/conversation_{customer_id}_{timestamp}.json`.
- `consolidate_conversations()` reads all `conversation_*.json` files in that directory and writes `conversation_data/consolidated_conversations.json`.

### Query Classification Categories

**Week 1:** `technical`, `billing`, `return`, `warranty`, `product_information`, `installation`, `financing`, `general_information`

**Week 2:** `technical_support`, `billing`, `returns`, `product_inquiry`, `general_information`

Urgency levels (both weeks): `low`, `medium`, `high` — high urgency overrides routing to "Priority Support Team" (Week 1) or sets `resolution_status=escalated` (Week 2).
