from __future__ import annotations
import json
import os
import anthropic
from app.auth import ubersuggest_oauth as ub_oauth

_client: anthropic.Anthropic | None = None

_UBERSUGGEST_MCP_URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
_UBERSUGGEST_MCP_NAME = "ubersuggest"

SYSTEM_TEMPLATE = """You are a B2B growth consultant for Komacut (online laser cutting, sheet metal fabrication, CNC machining — US/Canada market).
You have just completed a PPC and SEO audit. Answer the user's question concisely and specifically, referencing actual data from the audit findings below.
Be direct, actionable, and avoid filler. Use bullet points when listing items.
You have access to Ubersuggest SEO tools — use them when the user asks about keyword research, search volumes, competition, or content ideas.

AUDIT FINDINGS SUMMARY:
{context}"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _mcp_server() -> dict:
    server: dict = {
        "type": "url",
        "url": _UBERSUGGEST_MCP_URL,
        "name": _UBERSUGGEST_MCP_NAME,
    }
    token = ub_oauth.get_token() or os.environ.get("UBERSUGGEST_API_KEY")
    if token:
        server["authorization_token"] = token
    return server


def _build_context(audit: dict) -> str:
    ppc = audit["ppc"]
    seo = audit["seo"]
    return f"""PPC: ${ppc['summary']['waste_total_usd']} wasted ({ppc['summary']['waste_keywords_count']} zero-conv keywords), {ppc['summary']['high_cpa_count']} high-CPA keywords, {ppc['summary']['winners_count']} winners below $120 CPA, {ppc['summary']['negative_kw_candidates_count']} negative KW candidates.
SEO: {seo['summary']['quick_wins_count']} quick-win keywords (pos 4-20), {seo['summary']['near_opportunities_count']} near-opportunities (pos 21-50), {seo['summary']['competitor_gaps_count']} competitor gap keywords.

Top waste keywords: {', '.join(r['keyword'] for r in ppc['waste_spend'][:5])}
Top winners: {', '.join(r['keyword'] + ' ($' + str(round(r['cost_per_conv'])) + '/conv)' for r in ppc['winners'][:5])}
Negative KW candidates: {', '.join(r['search_term'] for r in ppc['negative_kw_candidates'][:6])}
SEO quick wins: {', '.join(r['Keywords'] + ' (#' + str(r['Position']) + ')' for r in seo['quick_wins'])}
Top competitor gaps: {', '.join(r['Keyword'] for r in seo['competitor_gaps'][:5])}"""


def reply(message: str, audit: dict, history: list[dict] | None = None) -> str:
    client = _get_client()
    context = _build_context(audit)
    system = SYSTEM_TEMPLATE.format(context=context)

    # Build full message list: prior turns + current user message
    messages = list(history or []) + [{"role": "user", "content": message}]

    ubersuggest_token = ub_oauth.get_token() or os.environ.get("UBERSUGGEST_API_KEY")

    if ubersuggest_token:
        response = client.beta.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=system,
            messages=messages,
            mcp_servers=[_mcp_server()],
            tools=[{"type": "mcp_toolset", "mcp_server_name": _UBERSUGGEST_MCP_NAME}],
            betas=["mcp-client-2025-11-20"],
        )
        text_block = next(
            (block for block in response.content if block.type == "text"), None
        )
        return text_block.text if text_block else ""
    else:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=system,
            messages=messages,
        )
        return response.content[0].text
