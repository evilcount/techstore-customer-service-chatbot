# TechStore Plus — Customer Service Chatbot

Multi-week capstone project implementing a customer service chatbot for **TechStore Plus**, a fictional e-commerce tech store. The project evolves across weeks, each adding a new layer of architecture.

---

## Project Structure

```
techstore-chatbot/
├── TechStorePlus_Customer_Service_Chatbot_Project.ipynb   # Week 1 — OpenAI direct
├── TechStorePlus_LangChain_LCEL_Chatbot.ipynb             # Week 2 — LangChain LCEL
├── conversation_data/                                      # Generated JSON files
│   ├── conversation_<customer_id>_<timestamp>.json
│   └── consolidated_conversations.json
├── requirements.txt
├── .env                                                    # API keys (not committed)
└── .venv/                                                  # Virtual environment
```

---

## Environment Setup

```powershell
# Create and activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...

# Optional — enables LangSmith tracing for Week 2
LANGCHAIN_API_KEY=ls__...
```

---

## Week 1 — OpenAI Direct (`TechStorePlus_Customer_Service_Chatbot_Project.ipynb`)

Chatbot built calling the OpenAI API directly, without any framework.

### Architecture

```
user query
  → analyze_customer_query()          # gpt-4o-mini, temp=0 → structured JSON
  → generate_personalized_response()  # gpt-4o-mini, temp=0.4 → reply string
  → chatbot_reply()                   # orchestrates above two
  → generate_conversation_summary()   # gpt-4o-mini, temp=0.2 → JSON summary
  → save_conversation_json()          # writes conversation_data/<id>_<ts>.json
  → consolidate_conversations()       # merges all files → consolidated_conversations.json
```

### Key Components

| Component | Description |
|-----------|-------------|
| `COMPANY_CONTEXT` | Knowledge base dict injected into the system prompt |
| `SYSTEM_ROLE` | f-string system prompt with conversation flow (5 steps) |
| `ConversationSession` | Holds per-session message history including the system role |
| `analyze_customer_query()` | Returns 8-field JSON: sentiment, emotions, category, urgency, products, entities, routing, reasoning |
| `generate_personalized_response()` | Generates reply using conversation history + analysis |
| `chatbot_reply()` | Single entry point — calls analysis + response, returns combined dict |
| `generate_conversation_summary()` | Third LLM call that writes a free-text summary of the conversation |

### Query Categories

`technical` · `billing` · `return` · `warranty` · `product_information` · `installation` · `financing` · `general_information`

Urgency: `low` · `medium` · `high` — high urgency overrides routing to **Priority Support Team**.

### Mock Mode

Cell 9 (`MOCK_MODE = True`) overrides the three OpenAI functions with local rule-based equivalents (keyword matching + regex). No API calls are made. Useful for testing without consuming credits.

### Running

```powershell
jupyter notebook TechStorePlus_Customer_Service_Chatbot_Project.ipynb
```

Run cells top-to-bottom. Set `MOCK_MODE = True` in cell 9 to disable API calls.

### Test Cases (10 queries)

| Query | Category | Urgency |
|-------|----------|---------|
| iPhone 15 stock + shipping to Chicago | product_information | low |
| Emergency — order never arrived, need laptop tomorrow | general_information | high |
| Thank you + want to buy gaming headphones | general_information | low |
| Can't configure router | technical | low |
| Need receipt for order #TEC-2023-089 | billing | medium |
| Tablet bought 8 months ago won't turn on | warranty | medium |
| Laptop recommendation for engineering student, $800 budget | product_information | low |
| Urgently need to return incompatible phone | return | high |
| Install home theater downtown | installation | low |
| Interest-free installments for MacBook Pro, Visa accepted? | financing | low |

---

## Week 2 — LangChain LCEL (`TechStorePlus_LangChain_LCEL_Chatbot.ipynb`)

Refactoring of the Week 1 chatbot using LangChain's composable pipeline (LCEL) with Pydantic structured output.

### Architecture

```
Input: {"query": str, "customer_id": str}
  ↓
RunnablePassthrough.assign(analysis=lambda | analysis_chain)
  → Component 1: analysis_prompt | llm.with_structured_output(QueryAnalysis)
  ↓
RunnablePassthrough.assign(response=RunnableLambda(route_response))
  → Component 2: CATEGORY_PROMPTS[category] | response_llm
  ↓
RunnableLambda(build_summary)
  → Component 3: programmatic assembly → ConversationSummary

Output: ConversationSummary (Pydantic)
```

### Key Components

| Component | Description |
|-----------|-------------|
| `QueryAnalysis` | Pydantic model — category (5 options), urgency, sentiment, `ExtractedEntities` |
| `analysis_chain` | `analysis_prompt \| llm.with_structured_output(QueryAnalysis)`, temp=0 |
| `CATEGORY_PROMPTS` | Dict of 5 `ChatPromptTemplate`, one per category, each with a specialist persona |
| `route_response()` | `RunnableLambda` that selects the correct prompt at runtime and invokes it |
| `ConversationSummary` | Pydantic model matching the Week 1 JSON structure |
| `build_summary()` | Assembles summary deterministically from analysis — no extra LLM call |
| `full_chain` | Complete LCEL pipe connecting all three components |

### Query Categories (Week 2)

`technical_support` · `billing` · `returns` · `product_inquiry` · `general_information`

### Urgency → Resolution Status Mapping

| Urgency | Resolution Status |
|---------|------------------|
| `high` | `escalated` |
| `medium` | `pending` |
| `low` | `resolved` |

### LangSmith Tracing

Add `LANGCHAIN_API_KEY` to `.env`. Tracing is enabled automatically before any LLM is instantiated. Traces appear at `smith.langchain.com` under project `Advanced-Customer-Agent`.

> **Note:** `LANGCHAIN_TRACING_V2` and `LANGCHAIN_PROJECT` must be set **before** instantiating any `ChatOpenAI` object — LangChain reads these at creation time.

### Running

```powershell
jupyter notebook TechStorePlus_LangChain_LCEL_Chatbot.ipynb
```

Run cells top-to-bottom. LangSmith tracing is optional — the chain runs normally without it.

### Key Differences from Week 1

| Aspect | Week 1 | Week 2 |
|--------|--------|--------|
| JSON parsing | Manual + fallback cleanup | Pydantic via `with_structured_output()` |
| Routing logic | Inline in caller | Encapsulated in `RunnableLambda` |
| Conversation summary | 3rd LLM call | Deterministic (no API cost) |
| Observability | None | LangSmith traces with token counts per step |
| Schema validation | Silent failures possible | `ValidationError` raised on bad output |

---

## Week 4 — RAG Fundamentals (`Week4_RAG_TechStore.ipynb`)

Week 4 adds Retrieval-Augmented Generation to the TechStore Plus chatbot without
replacing the previous weeks. The RAG pipeline loads TechStore knowledge-base documents,
splits them into chunks, stores embeddings in ChromaDB, reloads the persisted vector
store, and answers customer questions using retrieved context.

### Architecture

```text
docs/knowledge_base/*
  → src.rag.document_loader.load_documents()
  → src.rag.text_splitter.split_documents()
  → src.rag.vector_store.TechStoreVectorStore
  → ChromaDB persisted under chroma_db/
  → src.rag.rag_chain.TechStoreRAGAssistant
  → grounded answer with source metadata
```

### Running

```powershell
pip install -r requirements.txt
jupyter notebook Week4_RAG_TechStore.ipynb
```

Create a `.env` file with `OPENAI_API_KEY` before running embedding or answer cells.
Generated ChromaDB files are local artifacts and are ignored by Git.

### What Week 4 Adds

| Capability | Description |
|------------|-------------|
| Document loading | Supports `.md`, `.txt`, and `.pdf` files |
| Chunking | Uses recursive splitting with metadata preserved |
| Vector database | Persists embeddings in local ChromaDB |
| Grounded Q&A | Answers TechStore policy questions with retrieved context |
| Chatbot integration | Routes policy, warranty, shipping, returns, product, and support questions to RAG |

---

## Week 4 Mini Project — Python Library RAG (`Week4_RAG_Python_Library.ipynb`)

This mini project builds a RAG chatbot over the official Requests Python library
documentation. It fetches selected Requests docs pages, stores local `.txt` copies,
chunks the content, persists embeddings in a separate ChromaDB collection, answers
technical questions, and computes retrieval metrics.

### Running

```powershell
jupyter notebook Week4_RAG_Python_Library.ipynb
```

For a command-line chatbot:

```powershell
python scripts/requests_rag_chatbot.py --refresh --question "How do I set a timeout?"
```

The Requests docs are stored under:

```text
docs/python_library_docs/requests/
```

The vector store is generated locally under:

```text
chroma_db/requests_docs
```

The bonus evaluation includes macro Precision, Recall, F1 Score, and ROC curve points.

---

## Week 7 — LangGraph Challenge (`Week7_LangGraph_Challenge.ipynb`)

Module 3's first challenge: replaces the Week 3 agent's `create_react_agent` prebuilt loop with a
hand-rolled LangGraph `StateGraph` — typed state with reducers, a loop-cap guard, checkpointing, and
streamed observability, all explicit and testable instead of hidden inside a prebuilt call.

### Architecture

```text
Input: {"messages": [...], "tool_calls": 0, "retries": 0, "errors": []}
  ↓
START → agent
  agent → (tools | safe_exit | END)   via route_after_agent (tools_condition + loop-cap check)
  tools → agent                       (feed tool results back)
  safe_exit → END                     (loop cap tripped)
```

### Key Components

| Component | Description |
|-----------|-------------|
| `AgentState` | `TypedDict` — `messages` (`add_messages`), `tool_calls`/`retries` (`operator.add`), `errors` (`operator.add`) |
| `add`, `multiply` | Loosely-typed tools (`str \| float \| int`) that never raise; return `"ERROR:<CLASS>: ..."` strings on bad input |
| `route_after_agent` | Conditional edge combining `tools_condition` with the `MAX_TOOL_CALLS = 5` loop-cap check |
| `safe_exit` | Node reached only when the loop cap trips; appends a friendly message + structured error |
| `build_graph()` | Factory in `src/chains/langgraph_challenge_agent.py`; injectable `llm`/`checkpointer`/`interrupt_before` for testing |

### Running

```powershell
jupyter notebook Week7_LangGraph_Challenge.ipynb
```

Offline unit tests (fake LLM double, no API calls): `pytest tests/test_langgraph_challenge_agent.py -v`

### Note on the spec's worked example

The challenge document's math-chain acceptance test claims `"Add 2.5 and 7, then multiply by 3."`
returns `27.0`. That's arithmetically inconsistent — `(2.5 + 7) * 3 = 28.5`. The notebook and tests
validate the correct value (`28.5`) instead.

---

## Conversation Persistence

Both weeks share the same output format:

```json
{
  "timestamp": "2026-05-14T18:53:14",
  "customer_id": "CUST-78C546C3",
  "conversation_summary": "...",
  "query_category": "general_information",
  "customer_sentiment": "negative",
  "urgency_level": "high",
  "mentioned_products": ["Laptop"],
  "extracted_information": { "order_number": "#TEC-2024-001" },
  "resolution_status": "escalated",
  "actions_taken": ["..."],
  "follow_up_required": true
}
```

Individual files: `conversation_data/conversation_<customer_id>_<timestamp>.json`

Consolidated: `conversation_data/consolidated_conversations.json`

---

## Week 3 — Memory & Tools Agent (`src/chains/memory_agent.py`)

Extends the Week 2 LCEL chain with:
- **HybridMemory** (`src/components/hybrid_memory.py`) — capped message buffer + rolling summary for multi-turn conversations, one instance per customer email
- **MemoryAgent** (`src/chains/memory_agent.py`) — tool-using agent built on `langgraph.prebuilt.create_react_agent`, wired to the six customer tools in `src/components/customer_tools.py`
- **MCP server integration** — `src/mcp/notion_followup_server.py`

`MemoryAgent` uses `create_react_agent` as its loop, not a custom `StateGraph` — see
[Week 7](#week-7--langgraph-challenge-week7_langgraph_challengeipynb) for the hand-rolled `StateGraph`
version.
