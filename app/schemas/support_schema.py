from pydantic import BaseModel, EmailStr, Field


class SupportReplyRequest(BaseModel):
    """Input payload for customer support message analysis."""

    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_email: EmailStr
    message: str = Field(..., min_length=5, max_length=5000)
    product: str = Field(..., min_length=1, max_length=150)
    tone: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Preferred communication tone (for example: professional, friendly).",
    )


class SupportReplyResponse(BaseModel):
    """Structured support output that is ready for AI workflows."""

    customer_name: str
    category: str
    priority: str
    sentiment: str
    summary: str
    suggested_reply: str
    recommended_action: str
