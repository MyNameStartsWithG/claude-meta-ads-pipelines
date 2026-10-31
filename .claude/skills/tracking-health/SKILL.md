---
name: tracking-health
description: Health check for Meta pixel / Conversions API datasets and product catalogs - event volumes, Event Match Quality, event rules, custom conversions and catalog diagnostics. Read-only. Use for "is my pixel working", "conversions stopped coming in", "check CAPI", "catalog errors", /tracking-health.
---

# Pipeline 2: Tracking and catalog health (read-only)

This pipeline changes nothing. Do not call any write tool, including the pixel event rule tools.

## Steps
1. **Find datasets**: `ads_get_datasets` for the ad account (or business), then `ads_get_dataset_details` for each one, including its Conversions API setup.
2. **Event volume**: `ads_get_dataset_stats` for the last 7 and 28 days (28 days is the maximum window), broken down by source so browser and server events can be compared.
3. **Match quality**: `ads_get_dataset_quality`: Event Match Quality per event, match-key coverage and data freshness. Treat an EMQ below 6 out of 10 as weak.
4. **Event setup**: `ads_pixel_event_read` for the pixel's event rules and `ads_get_customconversions` for custom conversions on the ad account.
5. **Checklist**:
   - Is the funnel in order? More Purchase than AddToCart events points to a misfiring tag.
   - Do Purchase events carry `value` and `currency`?
   - When both browser and server send an event, does deduplication work (shared `event_id`)?
   - Has any key event been at zero for 24 hours?
   - Is any custom conversion used for optimization without recent activity?
6. **Catalogs** (if any): `ads_catalog_list_catalogs`, then for each one `ads_catalog_get_diagnostics`, `ads_catalog_get_dynamic_ads_health` and `ads_catalog_event_source_get_health` (match rate between pixel events and catalog products).
7. **Unclear errors**: look them up with `ads_get_help_article`.

## Output
Write `reports/tracking-YYYY-MM-DD.md`: a ✅ / ⚠️ / ❌ line for each check, the finding, and a fix specific enough to hand to a developer.
