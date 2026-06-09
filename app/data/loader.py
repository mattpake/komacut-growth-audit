from pathlib import Path
import pandas as pd

_DATA_DIR = Path(__file__).parent.parent.parent
_PPC_DIR = _DATA_DIR / "komacut_google_ads_mock"
_SEO_FILE = _DATA_DIR / "komacut_ubersuggest_master_input.xlsx"

# Cached after first load
_cache: dict | None = None


def _pct(series: pd.Series) -> pd.Series:
    """'3.45%' -> 0.0345, already float passthrough."""
    if series.dtype == object:
        return series.str.rstrip("%").astype(float) / 100
    return series


def _money(series: pd.Series) -> pd.Series:
    """'$1.23' or '1.23' -> float."""
    if series.dtype == object:
        return series.str.replace("[$,]", "", regex=True).astype(float)
    return series


def _clean_ppc(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "Impr.": "impressions",
        "Clicks": "clicks",
        "CTR": "ctr",
        "Avg. CPC": "avg_cpc",
        "Cost": "cost",
        "Conversions": "conversions",
        "Conv. rate": "conv_rate",
        "Cost / conv.": "cost_per_conv",
        "Conv. value": "conv_value",
        "ROAS": "roas",
        "Ad group": "ad_group",
        "Match type": "match_type",
        "Search term": "search_term",
        "Ad type": "ad_type",
        "Headline 1": "headline_1",
        "Headline 2": "headline_2",
        "Headline 3": "headline_3",
        "Description 1": "description_1",
        "Description 2": "description_2",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    for col in ("ctr", "conv_rate"):
        if col in df.columns:
            df[col] = _pct(df[col])

    for col in ("avg_cpc", "cost", "cost_per_conv", "conv_value", "roas"):
        if col in df.columns:
            df[col] = _money(df[col])

    for col in ("impressions", "clicks", "conversions"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def load() -> dict:
    global _cache
    if _cache is not None:
        return _cache

    campaigns = _clean_ppc(pd.read_csv(_PPC_DIR / "campaign_performance_komacut_mock.csv"))
    keywords = _clean_ppc(pd.read_csv(_PPC_DIR / "keyword_performance_komacut_mock.csv"))
    search_terms = _clean_ppc(pd.read_csv(_PPC_DIR / "search_terms_komacut_mock.csv"))
    ads = _clean_ppc(pd.read_csv(_PPC_DIR / "ad_performance_komacut_mock.csv"))

    xl = pd.ExcelFile(_SEO_FILE)
    rankings = xl.parse("Current Rankings")
    top_pages = xl.parse("Top Pages")
    kw_suggestions = xl.parse("Keyword Suggestions")
    gap_xometry = xl.parse("Gap Xometry")
    gap_protolabs = xl.parse("Gap Protolabs")
    priority_seeds = xl.parse("Priority Seeds")

    _cache = {
        "campaigns": campaigns,
        "keywords": keywords,
        "search_terms": search_terms,
        "ads": ads,
        "rankings": rankings,
        "top_pages": top_pages,
        "kw_suggestions": kw_suggestions,
        "gap_xometry": gap_xometry,
        "gap_protolabs": gap_protolabs,
        "priority_seeds": priority_seeds,
    }
    return _cache


def reset() -> None:
    global _cache
    _cache = None
