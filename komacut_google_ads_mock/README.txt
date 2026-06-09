Komacut Google Ads Mock Exports

Purpose:
These are synthetic Google Ads-style CSV exports prepared for a presales MVP demo for komacut.com.

They are NOT real Google Ads data.
They are designed to test:
- CSV upload/parsing
- PPC audit rules
- AI recommendations
- SEO/PPC opportunity report generation
- XLSX/PDF export

Recommended demo settings:
- Target CPA: 120 USD
- Currency: USD
- Goal: Lead generation / quote requests
- Brand: Komacut
- Market: US / Canada

Files:
1. campaign_performance_komacut_mock.csv
2. keyword_performance_komacut_mock.csv
3. search_terms_komacut_mock.csv
4. ad_performance_komacut_mock.csv

Built-in demo findings:
- Winning areas:
  - laser cutting services
  - custom sheet metal parts
  - online sheet metal fabrication
  - custom metal parts
  - metal laser cutting service

- Waste spend / negative keyword candidates:
  - free laser cutting files
  - laser cutting machine for sale
  - diy sheet metal bending
  - cnc machining course
  - laser cutting jobs
  - sheet metal design pdf
  - what is cnc machining
  - prototype template
  - protolabs careers
  - xometry coupon code

- High CPA / questionable areas:
  - competitor terms
  - contract manufacturing China/Mexico
  - broad educational CNC queries
  - broad sheet metal design/drawing queries

Suggested MVP logic:
- Waste spend: Cost > target CPA and Conversions = 0
- High CPA: Cost / conv. > target CPA
- Negative keyword candidate: Search term with 0 conversions or containing words like free, jobs, course, pdf, template, machine for sale, diy, careers, coupon
- Winner: Conversions > 0 and Cost / conv. < target CPA
- Low CTR ad: CTR < 3% for search ads or CTR < 1% for display/remarketing
