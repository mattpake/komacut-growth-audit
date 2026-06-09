# Komacut Growth Audit — Build Tracker

One feature per commit. Update this file after every feature is done.

---

## Feature Plan

| # | Feature | Status |
|---|---------|--------|
| 1 | Scaffold — deps, .gitignore, whats_done.md | ✅ Done |
| 2 | Data loader — parse CSVs + XLSX into DataFrames | ⬜ Pending |
| 3 | PPC audit engine — rules, findings JSON | ⬜ Pending |
| 4 | SEO audit engine — rules, findings JSON | ⬜ Pending |
| 5 | FastAPI shell + Jinja2 UI template | ⬜ Pending |
| 6 | `/audit/run` route — wires loader + engines | ⬜ Pending |
| 7 | AI recommendations — Claude call, structured output | ⬜ Pending |
| 8 | `/chat` endpoint — stateless Claude chat | ⬜ Pending |
| 9 | `/export/xlsx` — XLSX report download | ⬜ Pending |
| 10 | README + `.env.example` — final cleanup | ⬜ Pending |

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
