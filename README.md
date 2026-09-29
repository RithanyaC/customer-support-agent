# Customer Support Agent

## Project overview
This project is a minimal e-commerce customer support agent built with Python, LangGraph, SQLite, an MCP server, a local RAG policy system, and an optional Tavily search integration for external courier disruption and recall checks. It handles routine order status, shipment, return, refund, and policy questions while escalating repeated, negative, or explicit manager requests to a human handoff.

## Architecture
- SQLite stores mock customer, order, shipment, return, and refund data.
- MCP exposes the required business tools: `get_order`, `track_shipment`, and `initiate_return`.
- LangGraph orchestrates triage, order handling, policy checks, complaints, and escalation.
- Local RAG reads `data/policies.txt` and retrieves relevant policy text before making a rule-based decision.
- Tavily is used only for external courier disruption and product recall checks when available.

## Folder structure
- `app/` application code
- `app/agents/` LangGraph agent nodes
- `app/graph/` state and workflow definition
- `app/mcp_server/` MCP server implementation
- `app/rag/` local RAG policy index
- `app/tools/` Tavily wrapper
- `app/database/` SQLite access and seeding logic
- `data/` database and policy files
- `tests/` automated validation

## Requirements
- Python 3.11+
- Windows PowerShell
- Local environment with dependencies installed from `requirements.txt`

## Python version
Use Python 3.11 or newer.

## Virtual environment creation
```powershell
cd d:\Downloads-D\paper_comparison\selection\customer_support
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Dependency installation
```powershell
pip install -r requirements.txt
```

## Environment variables
Create a `.env` file based on `.env.example`.

```powershell
Copy-Item .env.example .env
```

The example file contains:
```env
OPENAI_API_KEY=
TAVILY_API_KEY=
```

## Database seeding
```powershell
python -m app.database.seed
```

## MCP server execution
```powershell
python -m app.mcp_server.server
```

## Application execution
```powershell
python -m app.main
```

## Test execution
```powershell
pytest -q
```

## Test customer IDs
- `CUST001` is the primary test customer.
- `CUST002` is used for unauthorized access testing.

## Test orders
- `10245` is the required test order for `CUST001`.
- Additional mock orders are seeded to cover delayed, cancelled, refunded, delivered, and return-related cases.

## Sample queries
- `Where is my order #10245?`
- `I want to return the shoes I bought last week.`
- `My refund still hasn't arrived after 10 days.`
- `This is the third time my order is late. I want to speak to a manager.`

## LangGraph architecture
The workflow uses a `StateGraph` and contains the following required nodes:
1. Triage Router
2. Order Agent
3. Policy Agent
4. Complaint Agent
5. Human Handoff Node

## MCP architecture
The MCP server exposes exactly the required tools:
- `get_order`
- `track_shipment`
- `initiate_return`

## RAG architecture
The RAG implementation loads `data/policies.txt`, chunks the text, vectorizes it using TF-IDF, and retrieves the most relevant sections before a policy-based decision is made.

## Tavily usage
Tavily is used only for courier disruption and product recall checks. It is optional and fails safely when the API key is missing or the request fails.

## Security and guardrails
- Order ownership is checked before any order, shipment, or refund data is returned.
- Another customer’s private data is never exposed.
- Policy eligibility must be confirmed before a return is created.
- Refund promises only follow the documented policy.
- Human escalation stops automated processing when issues are repeated, negative, or explicitly escalated.
