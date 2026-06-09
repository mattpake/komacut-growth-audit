from __future__ import annotations
import json
import os
import anthropic

_client: anthropic.Anthropic | None = None

SYSTEM_PROMPT = """You are a B2B growth consultant specialising in PPC and SEO for custom manufacturing companies.
You will receive audit findings for Komacut (online laser cutting, sheet metal fabrication, CNC machining — US/Canada market).
Return ONLY a valid JSON array of recommendation objects. No markdown, no prose, just the JSON array.

Each object must have exactly these fields:
{
  "priority": "High" | "Medium" | "Low",
  "module": "PPC" | "SEO" | "Competitor",
  "area": string (short area name e.g. "Negative Keywords", "Quick-Win SEO"),
  "problem": string (1-2 sentences describing the issue with evidence),
  "recommendation": string (1-2 sentences of the specific action),
  "next_action": string (imperative, under 15 words — the single most immediate step),
  "risk": "Low" | "Medium" | "High"
}

Rules:
- Generate 10–15 recommendations covering PPC waste, PPC high-CPA, negative keywords, SEO quick-wins, competitor gaps.
- Sort by priority: High first, then Medium, then Low.
- Be specific: reference actual keyword names, dollar amounts, and position numbers from the findings.
- Keep each field concise and actionable."""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _build_context(ppc: dict, seo: dict) -> str:
    return f"""PPC AUDIT FINDINGS:
- Wasted budget: ${ppc['summary']['waste_total_usd']} across {ppc['summary']['waste_keywords_count']} zero-conversion keywords
- High CPA keywords (above $120 target): {ppc['summary']['high_cpa_count']}
- Negative keyword candidates: {ppc['summary']['negative_kw_candidates_count']}
- Winning keywords (below $120 CPA): {ppc['summary']['winners_count']}
- Low CTR ads: {ppc['summary']['low_ctr_ads_count']}

WASTE SPEND KEYWORDS (top 5):
{json.dumps(ppc['waste_spend'][:5], indent=2)}

HIGH CPA KEYWORDS (top 5):
{json.dumps(ppc['high_cpa'][:5], indent=2)}

NEGATIVE KW CANDIDATES:
{json.dumps(ppc['negative_kw_candidates'][:8], indent=2)}

WINNING KEYWORDS (top 5):
{json.dumps(ppc['winners'][:5], indent=2)}

SEO AUDIT FINDINGS:
- Quick-win keywords (pos 4-20): {seo['summary']['quick_wins_count']}
- Near-opportunity keywords (pos 21-50): {seo['summary']['near_opportunities_count']}
- Weak pages (backlinks but low visits): {seo['summary']['weak_pages_count']}
- Competitor gap keywords: {seo['summary']['competitor_gaps_count']}

QUICK WIN KEYWORDS:
{json.dumps(seo['quick_wins'], indent=2)}

NEAR OPPORTUNITIES:
{json.dumps(seo['near_opportunities'], indent=2)}

TOP COMPETITOR GAPS (top 5):
{json.dumps(seo['competitor_gaps'][:5], indent=2)}

Generate 10-15 prioritised recommendations based on the above data."""


def generate(ppc: dict, seo: dict) -> list[dict]:
    client = _get_client()
    context = _build_context(ppc, seo)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    recommendations = json.loads(raw)
    return recommendations
