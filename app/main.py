from fastapi import FastAPI, HTTPException

from app.schemas.support_schema import SupportReplyRequest, SupportReplyResponse
from app.services.support_service import (
    MissingOpenAIApiKeyError,
    OpenAIRequestFailedError,
    generate_support_reply,
)

# Create the FastAPI application instance.
app = FastAPI(
    title="AI Customer Support Bot API",
    description="A portfolio backend API that transforms customer support messages into AI-ready structured responses.",
    version="0.2.0",
)


@app.get("/health")
def health_check() -> dict:
    """Simple health endpoint for quick service checks."""
    return {"status": "ok"}


@app.post("/generate-support-reply", response_model=SupportReplyResponse)
def generate_support_reply_endpoint(
    payload: SupportReplyRequest,
) -> SupportReplyResponse:
    """
    Generate a structured support response from customer input using OpenAI.

    Returns 503 if OpenAI is not configured, 502 if the upstream OpenAI call fails.
    """
    try:
        return generate_support_reply(payload)
    except MissingOpenAIApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OpenAIRequestFailedError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
