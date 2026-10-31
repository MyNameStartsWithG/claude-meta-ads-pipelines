---
name: ads-audit
description: Performance audit of a Meta ad account. Pulls campaigns, ad sets and ads, trends, anomalies, delivery errors, recent changes and industry benchmarks, then writes a report under reports/. Read-only. Use for "analyze my ads", "how are my campaigns doing", "weekly ads report", /ads-audit.
---

# Pipeline 1: Performance audit (read-only)

This pipeline changes nothing. Do not call any write tool.

## Input
- Ad account: if the user did not name one, list them with `ads_get_ad_accounts`; ask if there is more than one.
- Period: last 7 days compared with the 7 days before, unless the user says otherwise.

## Steps
1. **Context**: `ads_insights_advertiser_context` (industry, funnel) and `ads_get_opportunity_score` (0–100 score with Meta's recommendations).
2. **Inventory and metrics**: `ads_get_ad_entities` for active campaigns, ad sets and ads with spend, impressions, CTR, CPC, CPM, results, cost per result and ROAS. Count paused ones separately and leave them out of the analysis.
3. **Trends**: `ads_insights_performance_trend` for each active campaign.
4. **Anomalies**: `ads_insights_anomaly_signal` for KPIs that moved away from their baseline.
5. **Benchmarks**: `ads_insights_industry_benchmark` and `ads_insights_auction_ranking_benchmarks`.
6. **Delivery problems**: `ads_get_errors` for anything blocking delivery.
7. **Recent changes**: `ads_account_get_activity_logs` for the period, so a jump in cost can be tied to an edit (budget, targeting, new creative) rather than guessed at.
8. **Diagnosis**: give each problem a likely cause, for example:
   - creative fatigue: frequency above 3 and CTR falling
   - audience saturation: CPM rising while reach flattens
   - learning reset: a significant edit in the activity log right before the drop
   - tracking break: conversions drop to zero while clicks continue (suggest `tracking-health`)

## Output
Write `reports/audit-YYYY-MM-DD.md` with these sections:
- **Summary**: three bullets: best performer, worst performer, most urgent fix.
- **KPI table**: metrics per campaign and change against the previous period (%).
- **Anomalies and errors**: what Meta flagged and your diagnosis.
- **Recommendations**: in priority order, each with expected impact and the pipeline that would apply it (`budget-optimizer`, `audience-builder`, `campaign-launch`).

In chat, give only the summary and the file path. Never invent numbers: if a metric did not come back from a tool, write "no data".
