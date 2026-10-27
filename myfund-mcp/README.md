# MyFund Portfolio MCP

Private, read-only MCP server for the myfund.pl portfolio API.

## Tools

- `get_portfolio(portfel)` — returns the complete JSON payload for a named myfund portfolio.
- `get_portfolio_section(portfel, sekcja)` — returns one supported section: `portfel`, `tickers`, `struktura`, `strukturaWalory`, `zyskWCzasie`, `wartoscWCzasie`, `wkladWCzasie`, `benchWCzasie`, `stopaZwrotuWCzasie`, or `zmianaDzienna`.

## Run locally

Python 3.11+:

```bash
cd myfund-mcp
python -m venv .venv
# activate the virtual environment
pip install -e .
export MYFUND_API_KEY="your-myfund-key"
export MCP_ACCESS_TOKEN="a-long-random-bearer-token"
python server.py
``

The MCP endpoint is `http://localhost:8000/mcp`; the non-sensitive health endpoint is `http://localhost:8000/health`.

## Deploy on a free managed MCP host

The code is in the `myfund-mcp/` subdirectory of branch `myfund-mcp` in `KarolKurzyna/BI-Projects`. On a host that supports Python monorepos, set its project/root directory to `myfund-mcp` and start command to `python server.py`. Add these as encrypted environment secrets in the host dashboard:

- `MYFUND_API_KEY` — the newly generated myfund API key.
- `MCP_ACCESS_TOKEN` — a long random secret of your own, used as the Bearer token for all MCP requests.

Never commit real keys to GitHub or place them in a URL. The API key was deliberately not included in this repository.

## Security and limits

All MCP calls require `Authorization: Bearer <MCP_ACCESS_TOKEN>`. The health endpoint only reports whether secrets are configured, never their values. Upstream myfund responses may be cached by myfund for five minutes. The server is read-only and makes no portfolio changes.
