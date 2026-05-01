import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI, RateLimitError

from app.schemas.support_schema import SupportReplyRequest, SupportReplyResponse

# Load .env early so OPENAI_API_KEY is available for this module.
load_dotenv()


class MissingOpenAIApiKeyError(Exception):
    """Raised when OPENAI_API_KEY is not configured (service unavailable)."""

    def __init__(self, message: str = "OpenAI is not configured: set OPENAI_API_KEY in your environment.") -> None:
        super().__init__(message)


class OpenAIRequestFailedError(Exception):
    """Raised when the OpenAI API call fails or returns unusable output (bad gateway)."""

    def __init__(self, message: str = "OpenAI request failed. Please try again later.") -> None:
        super().__init__(message)


_DEFAULT_MODEL = "gpt-4o-mini"

_SYSTEM_PROMPT = """You are an expert customer-support triage assistant.

Given the customer's message and context, analyze the case and respond with a single JSON object only (no markdown, no prose outside JSON).

The JSON must have exactly these keys and value types:
- "category": string, exactly one of:
  billing, technical_support, account_access, cancellation, feature_request, refund, general_question, other
- "priority": string, exactly one of: low, medium, high
- "sentiment": string, exactly one of:
  calm, confused, frustrated, angry, urgent, positive, neutral
- "summary": string, one or two sentences summarizing the issue for an internal ticket
- "suggested_reply": string, a draft reply to the customer using the requested tone; be helpful and accurate
- "recommended_action": string, one clear next step for the support or billing team

Rules:
- Choose category and sentiment based on the customer's message, not assumptions beyond the text.
- Match priority to business impact and urgency (billing errors and access lockouts are often high).
- Keep suggested_reply professional; use the customer's name naturally if appropriate.
- Output valid JSON only."""


def _get_openai_client() -> OpenAI:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise MissingOpenAIApiKeyError()
    return OpenAI(api_key=api_key)


def _parse_json_content(content: str) -> dict[str, Any]:
    text = content.strip()
    if not text:
        raise OpenAIRequestFailedError("OpenAI returned an empty response.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OpenAIRequestFailedError(f"OpenAI returned invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise OpenAIRequestFailedError("OpenAI returned a non-object JSON value.")
    return data


def generate_support_reply(payload: SupportReplyRequest) -> SupportReplyResponse:
    """
    Analyze the customer message via OpenAI and return a structured support response.

    Raises:
        MissingOpenAIApiKeyError: When OPENAI_API_KEY is missing (map to HTTP 503).
        OpenAIRequestFailedError: When OpenAI fails or output is invalid (map to HTTP 502).
    """
    client = _get_openai_client()
    model = (os.getenv("OPENAI_MODEL") or _DEFAULT_MODEL).strip() or _DEFAULT_MODEL

    user_content = (
        f"Customer name: {payload.customer_name}\n"
        f"Customer email: {payload.customer_email}\n"
        f"Product: {payload.product}\n"
        f"Preferred tone for suggested_reply: {payload.tone}\n\n"
        f"Customer message:\n{payload.message}"
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
    except (APIConnectionError, APITimeoutError, RateLimitError, APIError) as exc:
        raise OpenAIRequestFailedError(
            f"OpenAI request failed: {exc.__class__.__name__}: {exc}"
        ) from exc
    except Exception as exc:
        raise OpenAIRequestFailedError(f"Unexpected error calling OpenAI: {exc}") from exc

    choice = completion.choices[0].message.content
    if choice is None:
        raise OpenAIRequestFailedError("OpenAI returned no message content.")

    raw = _parse_json_content(choice)

    # Ensure customer_name matches the request (authoritative source).
    merged = {
        "customer_name": payload.customer_name,
        "category": raw.get("category"),
        "priority": raw.get("priority"),
        "sentiment": raw.get("sentiment"),
        "summary": raw.get("summary"),
        "suggested_reply": raw.get("suggested_reply"),
        "recommended_action": raw.get("recommended_action"),
    }

    try:
        return SupportReplyResponse.model_validate(merged)
    except Exception as exc:
        raise OpenAIRequestFailedError(
            f"OpenAI output did not match the expected schema: {exc}"
        ) from exc
