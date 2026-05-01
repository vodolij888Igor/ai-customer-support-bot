from app.schemas.support_schema import SupportReplyRequest, SupportReplyResponse


def _classify_category(message: str) -> str:
    """Classify support category using simple keyword matching."""
    text = message.lower()

    if any(keyword in text for keyword in ["charged", "billing", "refund", "invoice", "payment"]):
        return "billing"
    if any(keyword in text for keyword in ["bug", "error", "not working", "issue", "crash"]):
        return "technical"
    if any(keyword in text for keyword in ["cancel", "unsubscribe", "plan", "upgrade", "downgrade"]):
        return "account"
    return "general"


def _detect_priority(category: str, message: str) -> str:
    """Assign priority based on category and urgency words."""
    text = message.lower()
    urgent_words = ["urgent", "asap", "immediately", "right away", "angry", "frustrated"]

    if category == "billing":
        return "high"
    if any(word in text for word in urgent_words):
        return "high"
    if category == "technical":
        return "medium"
    return "low"


def _detect_sentiment(message: str) -> str:
    """Approximate customer sentiment with lightweight rules."""
    text = message.lower()

    if any(word in text for word in ["frustrated", "angry", "upset", "charged twice", "disappointed"]):
        return "frustrated"
    if any(word in text for word in ["thanks", "thank you", "appreciate"]):
        return "positive"
    return "neutral"


def _build_summary(message: str, category: str) -> str:
    """Create a short, structured summary from the original message."""
    trimmed = message.strip()

    # Provide a cleaner, portfolio-friendly summary for common billing complaints.
    if category == "billing" and "charged twice" in trimmed.lower():
        return "Customer reports being charged twice for a subscription."

    if len(trimmed) <= 90:
        return trimmed
    return f"{trimmed[:87]}..."


def _build_suggested_reply(customer_name: str, tone: str, category: str) -> str:
    """Generate a placeholder suggested reply based on tone and category."""
    normalized_tone = tone.lower().strip()

    if category == "billing":
        core = (
            "I am sorry for the billing issue. I will review your account details and help resolve "
            "the duplicate charge as quickly as possible."
        )
    elif category == "technical":
        core = (
            "Thanks for reporting this issue. I will investigate what is happening and guide you "
            "through the next steps to fix it."
        )
    elif category == "account":
        core = (
            "I can help with your account request. I will verify the account details and provide "
            "the best next step."
        )
    else:
        core = "Thanks for reaching out. I will review your message and help you with the next step."

    if normalized_tone == "professional":
        return f"Hi {customer_name}, thank you for contacting support. {core}"
    if normalized_tone == "friendly":
        return f"Hi {customer_name}! Thanks for reaching out. {core}"
    return f"Hello {customer_name}, {core}"


def _recommended_action(category: str) -> str:
    """Provide a clear action recommendation for support operations."""
    if category == "billing":
        return "Review billing history and issue a refund if duplicate charge is confirmed."
    if category == "technical":
        return "Collect error details, reproduce the issue, and escalate to engineering if needed."
    if category == "account":
        return "Verify account ownership and process the requested account change."
    return "Review message details and route the ticket to the correct support workflow."


def generate_support_reply(payload: SupportReplyRequest) -> SupportReplyResponse:
    """
    Main service function for generating the structured support response.

    This uses deterministic placeholder logic for portfolio/demo purposes.
    """
    category = _classify_category(payload.message)
    priority = _detect_priority(category, payload.message)
    sentiment = _detect_sentiment(payload.message)
    summary = _build_summary(payload.message, category)
    suggested_reply = _build_suggested_reply(payload.customer_name, payload.tone, category)
    recommended_action = _recommended_action(category)

    return SupportReplyResponse(
        customer_name=payload.customer_name,
        category=category,
        priority=priority,
        sentiment=sentiment,
        summary=summary,
        suggested_reply=suggested_reply,
        recommended_action=recommended_action,
    )
