from __future__ import annotations

from typing import Any

import httpx


def compact(value: str, limit: int = 500) -> str:
    return " ".join(value.split())[:limit]


def describe_provider_error(exc: Exception, *, limit: int = 500) -> str:
    """Return a concise API error without exposing request headers or keys."""

    if isinstance(exc, httpx.HTTPStatusError):
        return compact(_describe_httpx_error(exc), limit)

    status = getattr(exc, "status_code", None)
    body = getattr(exc, "body", None)
    detail = _extract_error_detail(body)
    if not detail:
        response = getattr(exc, "response", None)
        detail = _extract_response_detail(response)
    if not detail:
        detail = str(exc) or type(exc).__name__

    prefix = f"HTTP {status} " if status else ""
    return compact(f"{prefix}{detail}", limit)


def _describe_httpx_error(exc: httpx.HTTPStatusError) -> str:
    status = exc.response.status_code
    detail = _extract_response_detail(exc.response) or exc.response.text
    return f"HTTP {status} {detail}"


def _extract_response_detail(response: object) -> str:
    if response is None:
        return ""
    json_method = getattr(response, "json", None)
    if callable(json_method):
        try:
            return _extract_error_detail(json_method())
        except Exception:
            pass
    text = getattr(response, "text", "")
    return str(text) if text else ""


def _extract_error_detail(body: object) -> str:
    if isinstance(body, dict):
        error = body.get("error", body)
        if isinstance(error, dict):
            code = error.get("code") or error.get("type") or ""
            message = error.get("message") or error.get("detail") or ""
            if code and message:
                return f"{code}: {message}"
            return str(code or message)
        return str(error)
    if isinstance(body, str):
        return body
    return ""
