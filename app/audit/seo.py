from __future__ import annotations
import pandas as pd

COMMERCIAL_INTENT = ["Transactional", "Commercial"]


def _score_opportunity(row: pd.Series) -> str:
    """High/Medium/Low based on volume, CPC, and SEO difficulty."""
    vol = row.get("Search Volume", row.get("Volume", 0)) or 0
    cpc = row.get("CPC", 0) or 0
    diff = row.get("SEO Difficulty", 50) or 50
    if vol >= 500 and cpc >= 3.0 and diff <= 40:
        return "High"
    if vol >= 100 and cpc >= 1.0:
        return "Medium"
    return "Low"


def run(data: dict) -> dict:
    rankings: pd.DataFrame = data["rankings"]
    top_pages: pd.DataFrame = data["top_pages"]
    kw_suggestions: pd.DataFrame = data["kw_suggestions"]
    gap_x: pd.DataFrame = data["gap_xometry"]
    gap_p: pd.DataFrame = data["gap_protolabs"]

    # --- Quick-win keywords: ranking 4–20 ---
    quick_wins = rankings[
        rankings["Position"].between(4, 20)
    ][["Keywords", "Position", "Volume", "Est. Visits", "Ranking Url"]].copy()
    quick_wins["opportunity"] = "quick_win"

    # --- Near-opportunity keywords: ranking 21–50 ---
    near_opp = rankings[
        rankings["Position"].between(21, 50)
    ][["Keywords", "Position", "Volume", "Est. Visits", "Ranking Url"]].copy()
    near_opp["opportunity"] = "near_opportunity"

    # --- Weak pages: has backlinks but low/zero visits ---
    weak_pages = top_pages[
        (top_pages["Backlinks"] > 0) & (top_pages["Est. Visits"] <= 10)
    ][["Title", "URL", "Est. Visits", "Backlinks"]].copy()

    # --- High-value keyword suggestions (commercial intent, good CPC, manageable difficulty) ---
    kw_scored = kw_suggestions.copy()
    kw_scored["priority"] = kw_scored.apply(_score_opportunity, axis=1)
    # Use CPC as commercial-intent signal when Search Intent is missing
    commercial_mask = (
        kw_scored["Search Intent"].isin(COMMERCIAL_INTENT) |
        (kw_scored["CPC"] >= 2.0)
    )
    high_value_kw = kw_scored[
        (kw_scored["priority"].isin(["High", "Medium"])) & commercial_mask
    ][["Keyword", "Search Intent", "Search Volume", "CPC", "SEO Difficulty", "priority"]].copy()
    high_value_kw = high_value_kw.sort_values(
        ["priority", "Search Volume"], ascending=[True, False]
    )

    # --- Competitor gap: keywords Xometry ranks for that Komacut does not ---
    # Filter to commercially relevant gaps (CPC > 0, not position 1 already)
    gap_x_clean = gap_x[
        (gap_x["CPC"] > 0) &
        (gap_x["Volume"] >= 100) &
        (gap_x["Position"].isna() | (gap_x["Position"] > 20))
    ][["Keyword", "Volume", "Position", "CPC", "SEO Difficulty"]].copy()
    gap_x_clean["competitor"] = "Xometry"
    gap_x_clean["priority"] = gap_x_clean.apply(_score_opportunity, axis=1)

    gap_p_clean = gap_p[
        (gap_p["CPC"] > 0) &
        (gap_p["Volume"] >= 100) &
        (gap_p["Position"].isna() | (gap_p["Position"] > 20))
    ][["Keyword", "Volume", "Position", "CPC", "SEO Difficulty"]].copy()
    gap_p_clean["competitor"] = "Protolabs"
    gap_p_clean["priority"] = gap_p_clean.apply(_score_opportunity, axis=1)

    competitor_gaps = (
        pd.concat([gap_x_clean, gap_p_clean], ignore_index=True)
        .sort_values(["priority", "Volume"], ascending=[True, False])
        .head(30)
    )

    return {
        "quick_wins": quick_wins.to_dict(orient="records"),
        "near_opportunities": near_opp.to_dict(orient="records"),
        "weak_pages": weak_pages.to_dict(orient="records"),
        "high_value_keywords": high_value_kw.head(20).to_dict(orient="records"),
        "competitor_gaps": competitor_gaps.to_dict(orient="records"),
        "summary": {
            "quick_wins_count": len(quick_wins),
            "near_opportunities_count": len(near_opp),
            "weak_pages_count": len(weak_pages),
            "high_value_keywords_count": len(high_value_kw),
            "competitor_gaps_count": len(competitor_gaps),
        },
    }
