from fastmcp import FastMCP
import json, os, urllib.parse, urllib.request

mcp = FastMCP("myfund-portfolio")
SECTIONS = ["portfel", "tickers", "struktura", "strukturaWalory", "zyskWCzasie", "wartoscWCzasie", "wkladWCzasie", "benchWCzasie", "stopaZwrotuWCzasie", "zmianaDzienna"]

def _get(name: str) -> dict:
    key = os.environ.get("MYFUND_API_KEY")
    if not key:
        raise RuntimeError("MYFUND_API_KEY is not configured")
    query = urllib.parse.urlencode({"portfel": name, "apiKey": key, "format": "json"})
    request = urllib.request.Request("https://myfund.pl/API/v1/getPortfel.php?" + query, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    if isinstance(data.get("status"), dict) and data["status"].get("code") == 1:
        raise RuntimeError(str(data["status"].get("text", "myfund API error")))
    return data

@mcp.tool()
def get_portfolio(portfel: str) -> dict:
    """Pobierz pełne dane portfela z myfund.pl."""
    return _get(portfel.strip())

@mcp.tool()
def get_portfolio_section(portfel: str, sekcja: str) -> dict:
    """Pobierz jedną sekcję danych portfela z myfund.pl."""
    if sekcja not in SECTIONS:
        raise ValueError("Nieznana sekcja. Dostępne: " + ", ".join(SECTIONS))
    data = _get(portfel.strip())
    if sekcja not in data:
        raise ValueError("API nie zwróciło sekcji: " + sekcja)
    return {sekcja: data[sekcja]}

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
