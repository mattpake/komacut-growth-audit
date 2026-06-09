# Komacut Growth Audit

AI-powered PPC + SEO audit demo for Komacut (online laser cutting, sheet metal fabrication, CNC machining — US/Canada).

## What it does

1. Loads mock Google Ads data and Ubersuggest SEO data with one button click
2. Runs rule-based PPC audit — finds wasted budget, high-CPA keywords, negative keyword candidates, and winning segments
3. Runs rule-based SEO audit — surfaces quick-win rankings, near-opportunities, and competitor keyword gaps vs Xometry and Protolabs
4. Sends findings to Claude Sonnet → returns 10–15 prioritised recommendations
5. Chat interface to ask questions about the findings
6. Export full report as XLSX

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- An Anthropic API key (for AI recommendations and chat)

## Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/mattpake/komacut-growth-audit.git
cd komacut-growth-audit

# 2. Copy env file and add your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Install dependencies
uv sync

# 4. Place data files in the project root (already included in repo)
#    komacut_google_ads_mock/   <- 4 CSV files
#    komacut_ubersuggest_master_input.xlsx

# 5. Run the server
uv run python main.py
```

Open http://localhost:8000 in your browser.

## Usage

1. Click **"Load Demo Data & Run Audit"** — runs instantly, no uploads needed
2. Browse the **PPC Audit** tab — waste spend, high CPA, negative KW candidates, winners
3. Browse the **SEO Audit** tab — quick wins, near-opportunities, competitor gaps
4. Click **"Generate AI Recommendations"** — Claude analyses findings and returns a prioritised action plan
5. Use the **Chat** tab to ask specific questions (e.g. "Which keywords should I pause first?")
6. Click **"Export XLSX"** to download the full report

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Single-page UI |
| GET | /health | Health check |
| POST | /audit/run | Load demo data, run PPC + SEO engines, return findings JSON |
| POST | /audit/recommendations | Send findings to Claude, return structured recommendations |
| POST | /chat | Single-turn chat with findings as context |
| GET | /export/xlsx | Download 8-sheet XLSX report |

## Project Structure

```
app/
  main.py              <- FastAPI app + all routes
  data/
    loader.py          <- Load and clean CSVs + XLSX (cached in memory)
  audit/
    ppc.py             <- PPC rules engine
    seo.py             <- SEO rules engine
  ai/
    recommendations.py <- Claude structured recommendation generation
    chat.py            <- Claude stateless chat handler
  export/
    xlsx.py            <- 8-sheet XLSX report builder
  templates/
    index.html         <- Single-page UI (Tailwind CDN + Alpine.js CDN)
main.py                <- uvicorn entry point
```

## PPC Audit Rules

| Rule | Condition |
|------|-----------|
| Waste spend | Cost > $120 AND conversions = 0 |
| High CPA | Conversions > 0 AND cost/conv > $120 |
| Negative KW candidates | Search term contains trigger words: free, jobs, course, pdf, machine for sale, diy, template, careers, coupon, what is, cheap |
| Winners | Conversions > 0 AND cost/conv <= $120 |
| Low CTR ads | Search ads < 3% CTR |

## SEO Audit Rules

| Rule | Condition |
|------|-----------|
| Quick-win | Current ranking position 4-20 |
| Near-opportunity | Current ranking position 21-50 |
| Weak page | Page has backlinks but <= 10 estimated visits |
| Competitor gap | Xometry/Protolabs keyword with CPC > 0 and volume >= 100 |
