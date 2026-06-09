from __future__ import annotations
import hashlib
import base64
import json
import secrets
from pathlib import Path
from urllib.parse import urlencode
import httpx

_MCP_BASE = "https://ubersuggest-mcp.neilpatelapi.com"
_TOKEN_FILE = Path(__file__).parent.parent.parent / ".ubersuggest_token.json"

# In-memory PKCE state during the OAuth redirect: {state -> context dict}
_pending: dict[str, dict] = {}


def _discover() -> dict:
    url = f"{_MCP_BASE}/.well-known/oauth-authorization-server"
    r = httpx.get(url, timeout=10, follow_redirects=True)
    r.raise_for_status()
    return r.json()


def _register_client(meta: dict, redirect_uri: str) -> str:
    reg_ep = meta.get("registration_endpoint")
    if not reg_ep:
        return "komacut-growth-audit"
    try:
        r = httpx.post(reg_ep, json={
            "client_name": "Komacut Growth Audit",
            "redirect_uris": [redirect_uri],
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
        }, timeout=10)
        if r.is_success:
            return r.json()["client_id"]
    except Exception:
        pass
    return "komacut-growth-audit"


def build_auth_url(redirect_uri: str) -> str:
    """Discover OAuth metadata, register client, return authorization URL."""
    meta = _discover()
    client_id = _register_client(meta, redirect_uri)

    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)

    _pending[state] = {
        "code_verifier": code_verifier,
        "client_id": client_id,
        "token_endpoint": meta["token_endpoint"],
        "redirect_uri": redirect_uri,
    }

    scopes = meta.get("scopes_supported", [])
    params: dict = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if scopes:
        params["scope"] = " ".join(scopes)

    return f"{meta['authorization_endpoint']}?{urlencode(params)}"


def exchange_code(code: str, state: str) -> str:
    """Exchange authorization code for access token; persist it; return the token."""
    ctx = _pending.pop(state, None)
    if not ctx:
        raise ValueError("Invalid or expired OAuth state — try connecting again")

    r = httpx.post(ctx["token_endpoint"], data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": ctx["redirect_uri"],
        "client_id": ctx["client_id"],
        "code_verifier": ctx["code_verifier"],
    }, timeout=15)
    r.raise_for_status()

    token_data = r.json()
    _TOKEN_FILE.write_text(json.dumps(token_data))
    return token_data["access_token"]


def get_token() -> str | None:
    if _TOKEN_FILE.exists():
        try:
            return json.loads(_TOKEN_FILE.read_text()).get("access_token")
        except Exception:
            return None
    return None


def is_connected() -> bool:
    return get_token() is not None


def disconnect() -> None:
    if _TOKEN_FILE.exists():
        _TOKEN_FILE.unlink()
