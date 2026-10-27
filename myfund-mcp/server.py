from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("myfund-portfolio")
SECTIONS = [
    "portfel", "tickers", "struktura", "strukturaWalory", "zyskWCzasie",
    "wartoscWCzasie", "wkladWCzasie", "benchWCzasie", "stopaZwrotuWCzasie",
    "zmianaDzienna",
]


def _get(name: str) -> dict[str, Any]:
    key = os.environ.get("MYFUND_API_KEY")
    if not key:
        raise RuntimeError("MYFUND_API_KEY is not configured")
    query = urllib.parse.urlencode({"portfel": name, "apiKey": key, "format": "json"})
    request = urllib.request.Request(
        "https://myfund.pl/API/v1/getPortfel.php?" + query,
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    if isinstance(data.get("status"), dict) and data["status"].get("code") == 1:
        raise RuntimeError(str(data["status"].get("text", "myfund API error")))
    return data


@mcp.tool()
def get_portfolio(portfel: str) -> dict[str, Any]:
    """Pobierz pełne dane portfela z myfund.pl."""
    if not portfel or not portfel.strip() or len(portfel) > 200:
        raise ValueError("Podaj nazwę portfela o długości 1–200 znaków.")
    return _get(portfel.strip())


@mcp.tool()
def get_portfolio_section(portfel: str, sekcja: str) -> dict[str, Any]:
    """Pobierz jedną sekcję danych portfela z myfund.pl."""
    if not portfel or not portfel.strip() or len(portfel) > 200:
        raise ValueError("Podaj nazwę portfela o długości 1–200 znaków.")
    if sekcja not in SECTIONS:
        raise ValueError("Nieznana sekcja. Dostępne: " + ", ".join(SECTIONS))
    data = _get(portfel.strip())
    if sekcja not in data:
        raise ValueError("API nie zwróciło sekcji: " + sekcja)
    return {sekcja: data[sekcja]}


class AuthAndHealth:
    """Protect the MCP endpoint with a bearer token; expose a non-sensitive health check."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        if path == "/health":
            body = json.dumps({
                "ok": True,
                "service": "myfund-portfolio-mcp",
                "configured": {
                    "apiKey": bool(os.environ.get("MYFUND_API_KEY")),
                    "accessToken": bool(os.environ.get("MCP_ACCESS_TOKEN")),
                },
            }).encode()
            await send({"type": "http.response.start", "status": 200,
                        "headers": [(b"content-type", b"application/json; charset=utf-8")]})
            await send({"type": "http.response.body", "body": body})
            return

        expected = os.environ.get("MCP_ACCESS_TOKEN")
        supplied = dict(scope.get("headers", [])).get(b"authorization", b"").decode("latin1")
        if not expected:
            status, message = 503, "MCP_ACCESS_TOKEN is not configured"
        elif supplied != "Bearer " + expected:
            status, message = 401, "Unauthorized"
        else:
            return await self.app(scope, receive, send)

        body = json.dumps({"error": message}).encode()
        await send({"type": "http.response.start", "status": status,
                    "headers": [(b"content-type", b"application/json; charset=utf-8")]})
        await send({"type": "http.response.body", "body": body})


if __name__ == "__main__":
    import uvicorn

    app = AuthAndHealth(mcp.http_app(path="/mcp"))
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
