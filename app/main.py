from fastapi import FastAPI

from app.schemas.support_schema import SupportReplyRequest, SupportReplyResponse
from app.services.support_service import generate_support_reply


# Create the FastAPI application instance.
app = FastAPI(
    title="AI Customer Support Bot API",
    description="A portfolio backend API that transforms customer support messages into AI-ready structured responses.",
    version="0.1.0",
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
    Generate a structured support response from customer input.

    Note:
    This first version uses placeholder business logic only.
    """
    return generate_support_reply(payload)
