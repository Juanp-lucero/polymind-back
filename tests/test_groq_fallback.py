"""Groq model fallback when the configured model is retired."""

from types import SimpleNamespace

import httpx
import pytest
from groq import NotFoundError

from app.services import groq_service


def model_not_found() -> NotFoundError:
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return NotFoundError(
        "model_not_found", response=httpx.Response(404, request=request), body=None
    )


def fake_groq(monkeypatch, calls: list, unavailable: set[str]) -> None:
    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            if kwargs["model"] in unavailable:
                raise model_not_found()
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))]
            )

    class FakeGroq:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(groq_service, "Groq", FakeGroq)
    monkeypatch.setattr(groq_service, "GROQ_API_KEY", "fake-key")
    monkeypatch.setattr(groq_service, "_working_model", None)


def test_retired_model_falls_back(monkeypatch) -> None:
    calls: list = []
    monkeypatch.setattr(groq_service, "GROQ_MODEL", "llama-3.3-70b-versatile")
    fake_groq(monkeypatch, calls, {"llama-3.3-70b-versatile"})

    assert groq_service.generate_json("s", "u") == {"ok": True}
    assert [c["model"] for c in calls] == ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]
    assert calls[1]["extra_body"] == {"reasoning_effort": "low"}


def test_returns_none_when_no_model_is_available(monkeypatch) -> None:
    calls: list = []
    fake_groq(monkeypatch, calls, set(groq_service.candidate_models()) | {"openai/gpt-oss-20b"})

    assert groq_service.generate_json("s", "u") is None


def test_report_raises_when_no_model_is_available(monkeypatch) -> None:
    fake_groq(monkeypatch, [], {"openai/gpt-oss-120b", "openai/gpt-oss-20b"})
    monkeypatch.setattr(groq_service, "GROQ_MODEL", "openai/gpt-oss-120b")
    with pytest.raises(RuntimeError):
        groq_service.generate_ai_report({}, [], [])
