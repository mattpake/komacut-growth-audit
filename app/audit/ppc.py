from __future__ import annotations
import pandas as pd

TARGET_CPA = 120.0

NEGATIVE_KW_TRIGGERS = [
    "free", "jobs", "course", "pdf", "machine for sale",
    "diy", "wiki", "template", "careers", "coupon", "salary",
    "what is", "cheap", "hire",
]


def _has_trigger(text: str) -> str | None:
    t = text.lower()
    for trigger in NEGATIVE_KW_TRIGGERS:
        if trigger in t:
            return trigger
    return None


def run(data: dict) -> dict:
    kw: pd.DataFrame = data["keywords"]
    st: pd.DataFrame = data["search_terms"]
    ads: pd.DataFrame = data["ads"]
    campaigns: pd.DataFrame = data["campaigns"]

    # --- Waste spend: cost > TARGET_CPA and zero conversions ---
    waste_mask = (kw["cost"] > TARGET_CPA) & (kw["conversions"] == 0)
    waste = kw[waste_mask][["keyword", "campaign", "cost", "impressions", "clicks", "conversions"]].copy()
    waste_total = float(waste["cost"].sum())

    # --- High CPA: has conversions but cost/conv > TARGET_CPA ---
    high_cpa_mask = (kw["conversions"] > 0) & (kw["cost_per_conv"] > TARGET_CPA)
    high_cpa = kw[high_cpa_mask][["keyword", "campaign", "cost", "conversions", "cost_per_conv"]].copy()

    # --- Negative KW candidates from search terms ---
    neg_candidates = []
    for _, row in st.iterrows():
        trigger = _has_trigger(str(row["search_term"]))
        if trigger:
            neg_candidates.append({
                "search_term": row["search_term"],
                "campaign": row["campaign"],
                "cost": row["cost"],
                "conversions": row["conversions"],
                "trigger_word": trigger,
            })
    neg_df = pd.DataFrame(neg_candidates)

    # --- Winning segments: has conversions and cost/conv <= TARGET_CPA ---
    win_mask = (kw["conversions"] > 0) & (kw["cost_per_conv"] <= TARGET_CPA)
    winners = kw[win_mask][["keyword", "campaign", "conversions", "cost_per_conv", "cost"]].copy()
    winners = winners.sort_values("cost_per_conv")

    # --- Low CTR ads (search < 3%, display < 1%) ---
    search_ads = ads[ads["ad_type"].str.lower().str.contains("search", na=False)]
    low_ctr_search = search_ads[search_ads["ctr"] < 0.03][
        ["campaign", "ad_group", "headline_1", "ctr", "impressions", "conversions"]
    ].copy()

    # --- Budget reallocation: which campaigns waste the most vs earn the most ---
    camp_waste = campaigns[
        (campaigns["cost"] > TARGET_CPA) & (campaigns["conversions"] == 0)
    ][["campaign", "cost"]].copy()

    camp_win = campaigns[
        (campaigns["conversions"] > 0) & (campaigns["cost_per_conv"] <= TARGET_CPA)
    ][["campaign", "conversions", "cost_per_conv", "cost"]].sort_values("cost_per_conv").copy()

    return {
        "waste_spend": waste.to_dict(orient="records"),
        "waste_total": round(waste_total, 2),
        "high_cpa": high_cpa.to_dict(orient="records"),
        "negative_kw_candidates": neg_df.to_dict(orient="records") if not neg_df.empty else [],
        "winners": winners.to_dict(orient="records"),
        "low_ctr_ads": low_ctr_search.to_dict(orient="records"),
        "budget_reallocation": {
            "waste_campaigns": camp_waste.to_dict(orient="records"),
            "winning_campaigns": camp_win.to_dict(orient="records"),
        },
        "summary": {
            "waste_keywords_count": len(waste),
            "waste_total_usd": round(waste_total, 2),
            "high_cpa_count": len(high_cpa),
            "negative_kw_candidates_count": len(neg_candidates),
            "winners_count": len(winners),
            "low_ctr_ads_count": len(low_ctr_search),
        },
    }
