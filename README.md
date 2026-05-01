# AI Customer Support Bot (FastAPI Backend)

[![Tests](https://github.com/vodolij888Igor/ai-customer-support-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/vodolij888Igor/ai-customer-support-bot/actions/workflows/tests.yml)

Portfolio project backend for transforming raw customer support messages into AI-ready structured outputs using **OpenAI** for analysis and reply drafting.

## Project Overview

This project provides a clean, production-oriented FastAPI API that receives a customer support request and returns structured response metadata.  
The `POST /generate-support-reply` endpoint calls the **OpenAI API** to classify the message, infer sentiment and priority, and produce a suggested reply plus a recommended internal action.  
The output is designed to be consumed by AI automation workflows, CRM integrations, and internal support tooling.

## Business Use Case

Customer support teams often receive unstructured messages that require triage before action.  
This API standardizes each message into:

- Category (for routing)
- Priority (for urgency handling)
- Sentiment (for support context)
- Summary (for quick review)
- Suggested reply (for response drafting)
- Recommended action (for operations workflow)

This helps reduce manual triage time and improves consistency in support operations.

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn
- OpenAI API (`openai` Python SDK)
- python-dotenv (optional `.env` for local development)

## Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── schemas/
│   │   └── support_schema.py
│   └── services/
│       └── support_service.py
├── tests/
│   └── test_generate_support_reply.py
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Create and activate a virtual environment.
2. Install dependencies.
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (required for `/generate-support-reply`).
4. Run the FastAPI server.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server will be available at:

- API base URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

If `OPENAI_API_KEY` is missing, `POST /generate-support-reply` returns **503** with a clear error. If the OpenAI request fails or returns invalid structured data, the API returns **502**.

## Running Tests

Automated tests mock the OpenAI client so they do not call the real API and do not require a valid `OPENAI_API_KEY`.

```bash
pip install -r requirements.txt
pytest
```

## API Endpoint

### POST `/generate-support-reply`

Accepts a customer support message and returns a structured support response.

### Sample Request

```json
{
  "customer_name": "Sarah Johnson",
  "customer_email": "sarah@example.com",
  "message": "Hi, I was charged twice for my subscription this month. Can you help me fix this?",
  "product": "SaaS Subscription",
  "tone": "professional"
}
```

### Sample Response

```json
{
  "customer_name": "Sarah Johnson",
  "category": "billing",
  "priority": "high",
  "sentiment": "frustrated",
  "summary": "Customer reports being charged twice for a subscription.",
  "suggested_reply": "Hi Sarah Johnson, thank you for contacting support. I am sorry for the billing issue. I will review your account details and help resolve the duplicate charge as quickly as possible.",
  "recommended_action": "Review billing history and issue a refund if duplicate charge is confirmed."
}
```

## Screenshot

The screenshot below shows a successful POST /generate-support-reply request in FastAPI Swagger UI with a 200 response.

![Swagger UI successful customer support reply response](docs/images/swagger-support-reply-code-200.png)

## API Usage Examples

**Scenario:** A SaaS company ingests inbound customer support messages and needs to **classify** the issue, **detect sentiment**, **assign priority**, and **draft a professional reply**—all in a single structured response suitable for ticketing tools, CRMs, or human review.

### cURL

With the API running locally (`uvicorn app.main:app --reload`), send a JSON payload to the endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/generate-support-reply" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Sarah Johnson",
    "customer_email": "sarah@example.com",
    "message": "Hi, I was charged twice for my subscription this month. Can you help me fix this?",
    "product": "SaaS Subscription",
    "tone": "professional"
  }'
```

On Windows PowerShell, use `curl.exe` or invoke `Invoke-RestMethod` with the same URL, header, and JSON body.

### Example successful JSON response

A **200 OK** response body has this shape (values may vary slightly depending on the model output):

```json
{
  "customer_name": "Sarah Johnson",
  "category": "billing",
  "priority": "high",
  "sentiment": "frustrated",
  "summary": "Customer reports being charged twice for a subscription.",
  "suggested_reply": "Hi Sarah, thank you for contacting us. I am sorry about the duplicate charge. I will review your billing history and work with you to resolve this promptly.",
  "recommended_action": "Review billing history and issue a refund if duplicate charge is confirmed."
}
```

### Postman

1. Create a new request: method **POST**, URL **`http://127.0.0.1:8000/generate-support-reply`**.
2. Open **Headers** and add **`Content-Type`** = **`application/json`**.
3. Open **Body**, select **raw**, choose **JSON**, and paste the same JSON fields as in the cURL example (`customer_name`, `customer_email`, `message`, `product`, `tone`).
4. Click **Send**. For a successful call, verify the response includes **`customer_name`**, **`category`**, **`priority`**, **`sentiment`**, **`summary`**, **`suggested_reply`**, and **`recommended_action`**.

## Current Limitations

- Requires a valid `OPENAI_API_KEY` and network access to OpenAI
- No database persistence
- No authentication/authorization
- No rate limiting
- No frontend client

## Future Improvements

- Add configurable models, retries, and observability for OpenAI calls
- Add ticket persistence with PostgreSQL
- Add authentication and role-based access
- Add observability (structured logging + metrics)
- Expand automated test coverage (e.g. edge cases, contract tests)
- Add Docker and CI/CD pipeline

## Notes for Portfolio Reviewers

This version combines clean API design and Pydantic validation with **real OpenAI-powered** triage and reply generation.  
The service layer maps configuration and upstream failures to **503** / **502** at the HTTP layer.  
The codebase is organized for easy extension into a full AI-enabled support platform.
