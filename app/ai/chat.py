from __future__ import annotations
import json
import os
import anthropic

_client: anthropic.Anthropic | None = None

SYSTEM_TEMPLATE = """You are a B2B growth consultant for Komacut (online laser cutting, sheet metal fabrication, CNC machining — US/Canada market).
You have just completed a PPC and SEO audit. Answer the user's question concisely and specifically, referencing actual data from the audit findings below.
Be direct, actionable, and avoid filler. Use bullet points when listing items.

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


def reply(message: str, audit: dict) -> str:
    client = _get_client()
    context = _build_context(audit)
    system = SYSTEM_TEMPLATE.format(context=context)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": message}],
    )
    return response.content[0].text
