# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jupyter notebook-based customer service chatbot for **TechStore Plus** (fictional e-commerce tech store). The main implementation is entirely within `TechStorePlus_Customer_Service_Chatbot_Project.ipynb`.

## Environment Setup

The project uses a local `.venv` virtual environment.

```powershell
# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1

# Install dependencies (if starting fresh)
pip install openai python-dotenv
```

API key is loaded from `.env`:
```
OPENAI_API_KEY=<your-key>
```

## Running the Notebook

```powershell
jupyter notebook TechStorePlus_Customer_Service_Chatbot_Project.ipynb
```

Run cells top-to-bottom. The **Mock Mode cell** (section 9 in the notebook) overrides the OpenAI functions with local rule-based equivalents — set `MOCK_MODE = True` to run without consuming API credits.

## Architecture

### Execution Modes

Two modes exist, controlled by a cell midway through the notebook:

- **OpenAI mode** (default): `analyze_customer_query`, `generate_personalized_response`, and `generate_conversation_summary` all call `gpt-4o-mini`.
- **Mock mode** (`MOCK_MODE = True`): the same three functions are overridden in-cell with pure-Python keyword/regex implementations. No API calls are made.

### Core Data Flow

```
user query
  → analyze_customer_query()     # returns structured analysis JSON
  → generate_personalized_response()  # sends analysis + session history to model
  → chatbot_reply()              # orchestrates above two, returns combined result dict
  → generate_conversation_summary()   # produces structured JSON summary
  → save_conversation_json()     # writes to conversation_data/<customer_id>_<timestamp>.json
  → consolidate_conversations()  # merges all files into consolidated_conversations.json
```

### Key Classes and Functions

- `ConversationSession` — holds per-session message history (including system role); exposes `add_user_message`, `add_assistant_message`, `get_public_history`.
- `chatbot_reply(session, query)` — single entry point for processing a customer message.
- `COMPANY_CONTEXT` dict — the knowledge base injected into `SYSTEM_ROLE`. Edit here to change company info.
- `SYSTEM_ROLE` — f-string system prompt defining behavior and conversation flow.

### Conversation Persistence

- Each conversation saves to `conversation_data/conversation_{customer_id}_{timestamp}.json`.
- `consolidate_conversations()` reads all `conversation_*.json` files in that directory and writes `conversation_data/consolidated_conversations.json`.

### Query Classification Categories

`analyze_customer_query` classifies queries into: `technical`, `billing`, `return`, `warranty`, `product_information`, `installation`, `financing`, `general_information`.

Urgency levels: `low`, `medium`, `high` — high urgency overrides routing to "Priority Support Team".
