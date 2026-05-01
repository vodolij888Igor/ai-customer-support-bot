"""
API tests for POST /generate-support-reply.

OpenAI is never called: the client is mocked so tests run without a real API key.
"""

import json
import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "customer_name": "Sarah Johnson",
    "customer_email": "sarah@example.com",
    "message": "Hi, I was charged twice for my subscription this month. Can you help me fix this?",
    "product": "SaaS Subscription",
    "tone": "professional",
}

EXPECTED_RESPONSE_KEYS = (
    "customer_name",
    "category",
    "priority",
    "sentiment",
    "summary",
    "suggested_reply",
    "recommended_action",
)

ALLOWED_PRIORITIES = frozenset({"low", "medium", "high"})
ALLOWED_SENTIMENTS = frozenset(
    {
        "calm",
        "confused",
        "frustrated",
        "angry",
        "urgent",
        "positive",
        "neutral",
    }
)


def _mock_llm_json() -> dict:
    return {
        "category": "billing",
        "priority": "high",
        "sentiment": "frustrated",
        "summary": "Customer reports being charged twice for a subscription.",
        "suggested_reply": (
            "Hi Sarah, thank you for reaching out. I am sorry about the duplicate charge. "
            "I will help resolve this right away."
        ),
        "recommended_action": "Review billing history and issue a refund if duplicate charge is confirmed.",
    }


def _attach_openai_mock(mock_get_client: MagicMock) -> MagicMock:
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = json.dumps(_mock_llm_json())
    mock_client.chat.completions.create.return_value = mock_completion
    mock_get_client.return_value = mock_client
    return mock_client


@patch("app.services.support_service._get_openai_client")
def test_successful_request_returns_200(mock_get_client: MagicMock) -> None:
    _attach_openai_mock(mock_get_client)

    response = client.post("/generate-support-reply", json=VALID_PAYLOAD)

    assert response.status_code == 200


@patch("app.services.support_service._get_openai_client")
def test_success_response_contains_all_expected_fields(mock_get_client: MagicMock) -> None:
    _attach_openai_mock(mock_get_client)

    response = client.post("/generate-support-reply", json=VALID_PAYLOAD)
    data = response.json()

    assert response.status_code == 200
    for key in EXPECTED_RESPONSE_KEYS:
        assert key in data
        assert data[key] is not None
        assert str(data[key]).strip() != ""


@patch("app.services.support_service._get_openai_client")
def test_priority_is_allowed_value(mock_get_client: MagicMock) -> None:
    _attach_openai_mock(mock_get_client)

    response = client.post("/generate-support-reply", json=VALID_PAYLOAD)
    data = response.json()

    assert response.status_code == 200
    assert data["priority"] in ALLOWED_PRIORITIES


@patch("app.services.support_service._get_openai_client")
def test_sentiment_is_allowed_value(mock_get_client: MagicMock) -> None:
    _attach_openai_mock(mock_get_client)

    response = client.post("/generate-support-reply", json=VALID_PAYLOAD)
    data = response.json()

    assert response.status_code == 200
    assert data["sentiment"] in ALLOWED_SENTIMENTS


def test_missing_required_field_returns_422() -> None:
    bad = {**VALID_PAYLOAD}
    del bad["message"]

    response = client.post("/generate-support-reply", json=bad)

    assert response.status_code == 422


def test_invalid_email_returns_422() -> None:
    bad = {**VALID_PAYLOAD, "customer_email": "not-a-valid-email"}

    response = client.post("/generate-support-reply", json=bad)

    assert response.status_code == 422


@patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False)
def test_missing_openai_api_key_returns_503() -> None:
    response = client.post("/generate-support-reply", json=VALID_PAYLOAD)

    assert response.status_code == 503
    body = response.json()
    assert "detail" in body


@patch("app.services.support_service._get_openai_client")
def test_openai_api_failure_returns_502(mock_get_client: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = ValueError("simulated upstream failure")
    mock_get_client.return_value = mock_client

    response = client.post("/generate-support-reply", json=VALID_PAYLOAD)

    assert response.status_code == 502
    body = response.json()
    assert "detail" in body
