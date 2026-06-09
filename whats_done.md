# Komacut Growth Audit — Build Tracker

One feature per commit. Update this file after every feature is done.

---

## Feature Plan

| # | Feature | Status |
|---|---------|--------|
| 1 | Scaffold — deps, .gitignore, whats_done.md | ✅ Done |
| 2 | Data loader — parse CSVs + XLSX into DataFrames | ✅ Done |
| 3 | PPC audit engine — rules, findings JSON | ✅ Done |
| 4 | SEO audit engine — rules, findings JSON | ✅ Done |
| 5 | FastAPI shell + Jinja2 UI template | ✅ Done |
| 6 | `/audit/run` route — wires loader + engines | ✅ Done |
| 7 | AI recommendations — Claude call, structured output | ✅ Done |
| 8 | `/chat` endpoint — stateless Claude chat | ✅ Done |
| 9 | `/export/xlsx` — XLSX report download | ✅ Done |
| 10 | README + `.env.example` — final cleanup | ✅ Done |

---

## What We're Building

**Komacut AI PPC + SEO Growth Audit Demo**

A single FastAPI app that:
1. Loads mock Google Ads CSVs + Ubersuggest XLSX (demo data, no uploads)
2. Runs rule-based PPC audit (waste spend, high CPA, negative KW candidates, winning segments, low CTR)
3. Runs rule-based SEO audit (quick-win keywords ranks 4-20, near-opportunities 21-50, competitor gaps vs Xometry/Protolabs)
4. Sends findings to Claude Sonnet → returns prioritized recommendations (JSON)
5. Serves a single-page UI (Jinja2 + Tailwind CDN + Alpine.js CDN) with findings tables
6. Chat endpoint for Q&A about the audit findings
7. Exports full report as XLSX

**Stack:** Python 3.12 + uv + FastAPI + pandas + openpyxl + Anthropic SDK + Jinja2

**Not building:** auth, PDF export, file upload, live API integrations, DB

---

## Key Constants (from spec)

- Target CPA: $120 USD
- Waste spend rule: Cost > $120 AND Conversions = 0
- High CPA rule: Conversions > 0 AND Cost/conv. > $120
- Low CTR (search): < 3%
- Low CTR (display): < 1%
- SEO quick-win: position 4–20
- SEO near-opportunity: position 21–50
- Negative KW trigger words: free, jobs, course, pdf, machine for sale, diy, wiki

---

## Directory Layout

```
app/
  main.py              ← FastAPI app entry point
  data/
    loader.py          ← Load CSVs + XLSX into DataFrames
  audit/
    ppc.py             ← PPC rules engine
    seo.py             ← SEO rules engine
  ai/
    recommendations.py ← Claude structured recommendations
    chat.py            ← Claude chat handler
  export/
    xlsx.py            ← XLSX report builder
  templates/
    index.html         ← Single-page UI
data/                  ← Symlink / copy of mock data files
```

---

## Done Details

### Feature 1 — Scaffold (2026-06-10)
- `pyproject.toml`: added all deps (fastapi, uvicorn, pandas, openpyxl, anthropic, python-dotenv, jinja2, python-multipart)
- `.gitignore`: added `.env`, `*.xlsx`, `*.zip`, OS files
- `whats_done.md`: this file

### Feature 2 — Data Loader (2026-06-10)
- `app/data/loader.py`: loads 4 Google Ads CSVs + 6 Ubersuggest XLSX sheets
- Normalises column names, parses % and currency strings, caches result in memory
- Fixed pandas 3 string dtype detection (`pd.api.types.is_string_dtype`)

### Feature 3 — PPC Audit Engine (2026-06-10)
- `app/audit/ppc.py`: 5 rules against keywords/search_terms/ads DataFrames
- Findings: 8 waste keywords ($2,214 total), 12 high-CPA, 11 negative KW candidates, 15 winners, 5 low-CTR ads

### Feature 4 — SEO Audit Engine (2026-06-10)
- `app/audit/seo.py`: quick-wins, near-opportunities, weak pages, high-value KWs, competitor gaps
- Uses CPC >= $2 as commercial-intent proxy when Search Intent field is NaN

### Feature 5 — FastAPI Shell + UI (2026-06-10)
- `app/main.py`: FastAPI app, GET / serving Jinja2 template, GET /health
- `app/templates/index.html`: full single-page UI with Tailwind CDN + Alpine.js CDN
- Tabs: PPC Audit, SEO Audit, AI Recommendations, Chat
- All fetch calls wired to backend routes

### Feature 6 — /audit/run Route (2026-06-10)
- POST /audit/run: loads data, runs both engines, caches in `_audit_cache`
- Returns combined `{ppc, seo}` findings JSON

### Feature 7 — AI Recommendations (2026-06-10)
- `app/ai/recommendations.py`: sends findings to Claude Sonnet 4-6
- Returns JSON array of 10–15 recommendations with priority/module/problem/recommendation/next_action/risk
- POST /audit/recommendations route

### Feature 8 — /chat Endpoint (2026-06-10)
- `app/ai/chat.py`: compact context string + stateless Claude call
- POST /chat accepts `{message}`, returns `{reply}`

### Feature 9 — /export/xlsx (2026-06-10)
- `app/export/xlsx.py`: 8-sheet workbook with styled headers + auto-width
- Sheets: Executive Summary, PPC Waste Spend, PPC High CPA, Negative KW Candidates, PPC Winners, SEO Quick Wins, SEO Near Opportunities, Competitor Gaps
- GET /export/xlsx streams as file download (~14 KB)

### Feature 10 — README + .env.example (2026-06-10)
- `README.md`: setup instructions, usage, API routes, project structure, audit rules
- `.env.example`: template for ANTHROPIC_API_KEY
