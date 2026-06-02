# Production Chat Demo Design

## Scope

Build the first production-ready demo layer around the TechStore Plus Week 3 agent.
The goal is to let a real user open a public URL, enter a demo password, provide any
customer email, and chat with the memory-aware support agent through a web UI.

This increment adds a deployable backend, frontend, and PostgreSQL persistence. It does
not replace the existing notebooks, core `MemoryAgent`, Notion integration, or MCP stdio
server.

## Deployment Target

- Frontend: Vercel
- Backend: Render Web Service
- Database: Render PostgreSQL

The deployed demo should be accessible from a browser and behave like a real customer
support chat box.

## Architecture

Use a split app:

```text
Vercel
  Next.js frontend
    -> HTTPS requests
Render
  FastAPI backend
    -> MemoryAgent
    -> PostgreSQL
    -> optional Notion follow-up integration
```

Project structure:

```text
c03-t05-bruno-pieri-m1-challenge/
├── src/
│   ├── chains/
│   ├── components/
│   ├── database/
│   ├── integrations/
│   └── mcp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
└── tests/
```

`src/` remains the agent engine. `backend/` exposes the API and persistence layer.
`frontend/` provides the customer-facing chat UI.

## User Experience

Flow:

1. User opens the Vercel URL.
2. User enters a demo password.
3. User enters any customer email address.
4. User can optionally click quick demo emails such as:
   - `john.doe@company.com`
   - `sarah.smith@company.com`
   - `emily.brown@company.com`
5. User sends chat messages.
6. Frontend shows a loading state while the backend calls the agent.
7. Backend returns a complete assistant response.
8. Messages are persisted and can be reloaded for the active session.

New customer emails must work. If the email is not present in `MockCustomerDB`, the
agent still creates memory for that email and can respond as a new or guest customer.
Customer lookup tools may return "No account found" for unknown emails.

The UI should be operational, not a marketing landing page. It should show:

- `TechStore Plus Support` header.
- Demo password screen.
- Required customer email field.
- Optional demo customer shortcuts.
- Scrollable message history.
- Message composer with send button.
- Loading, empty, and backend error states.

## Backend API

Base behavior:

- All chat routes require a demo password header.
- Responses are non-streaming.
- Errors return structured JSON.
- Backend should not log secrets.

Endpoints:

```text
GET /health
```

Returns service status.

```text
POST /api/auth/demo
```

Validates the demo password.

Request:

```json
{
  "password": "..."
}
```

Response:

```json
{
  "ok": true
}
```

```text
POST /api/chat/sessions
```

Creates a new chat session for any email.

Request:

```json
{
  "customer_email": "new.customer@example.com"
}
```

Response:

```json
{
  "session_id": "...",
  "customer_email": "new.customer@example.com"
}
```

```text
GET /api/chat/sessions/{session_id}/messages
```

Returns persisted messages for a session.

```text
POST /api/chat/sessions/{session_id}/messages
```

Saves the user message, calls `MemoryAgent.chat(customer_email, message)`, saves the
assistant response, and returns the assistant response.

Request:

```json
{
  "message": "Hi, I need help choosing a laptop"
}
```

Response:

```json
{
  "session_id": "...",
  "assistant_message": "...",
  "created_at": "2026-06-02T..."
}
```

## Database

Use PostgreSQL with two tables:

`chat_sessions`

- `id`: UUID primary key
- `customer_email`: text, required
- `created_at`: timestamp
- `updated_at`: timestamp

`chat_messages`

- `id`: UUID primary key
- `session_id`: UUID foreign key
- `role`: text, `user` or `assistant`
- `content`: text
- `created_at`: timestamp

The first production demo may keep `MemoryAgent` instances in process while also saving
messages to PostgreSQL. Advanced memory reconstruction from persisted history is deferred
to a later increment.

## Configuration

Backend environment variables:

```env
OPENAI_API_KEY=...
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
DATABASE_URL=...
DEMO_PASSWORD=...
FRONTEND_ORIGIN=https://your-vercel-app.vercel.app
```

Frontend environment variables:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-render-backend.onrender.com
```

Local development should support `.env` files and documented commands.

## Security

Use a simple demo password for the first public deployment.

The frontend sends the password to the backend for validation and then includes it in chat
requests, for example:

```text
X-Demo-Password: ...
```

This is acceptable for a portfolio/demo deployment but is not a substitute for production
authentication. Future production hardening should add proper auth, rate limiting, and
admin controls.

## Testing

Add focused tests for:

- Demo password success and failure.
- Session creation for known and unknown emails.
- Message persistence.
- Chat endpoint calling an injected fake agent.
- Backend health endpoint.
- Frontend rendering of password screen, email field, and empty chat state.

Existing Week 3 tests must continue to pass.

## Deployment Documentation

Update README with:

- Local backend run command.
- Local frontend run command.
- Render backend setup.
- Render PostgreSQL setup.
- Vercel frontend setup.
- Required environment variables.
- Smoke test checklist after deployment.

## Increment 1 Non-Goals

- No token-by-token streaming.
- No admin dashboard.
- No full auth system.
- No customer account creation workflow.
- No advanced reconstruction of `HybridMemory` from PostgreSQL.
- No replacement of the existing MCP stdio server.
