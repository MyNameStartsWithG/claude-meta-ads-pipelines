---
name: audience-builder
description: Designs Meta audiences from a product brief and account data - broad / Advantage+, interest-based and warm or lookalike variants - and, once approved, creates them as paused ad sets, optionally inside an A/B test. Use for "build an audience", "who should I target", "test a new audience", /audience-builder.
---

# Pipeline 4: Audience builder

## Steps
1. **Brief**: get it from the user (ask for what is missing): product or service, price range, where it sells, ideal customer, campaign objective.
2. **What already works**: `ads_get_ad_entities` for the existing ad sets; use the targeting of the best cost-per-result ad sets as the reference. Add industry context from `ads_insights_advertiser_context`.
3. **Existing audiences**: `ads_get_ad_account_custom_audiences` (customer lists, website visitors, engagers, lookalikes) and `ads_get_custom_audience_adsets` to see which ones are already in use.
4. **Three variants**, clearly different from each other:
   - **A: Broad / Advantage+ audience**: location, age and language only; let delivery find the buyers.
   - **B: Interests**: 3–6 related interests around one theme. Use only interest IDs that come from a tool result (existing ad sets) or from the user. Never invent targeting IDs; if none are available, describe the theme as audience suggestions for Advantage+ instead.
   - **C: Warm or lookalike**: built on an existing custom audience. A new lookalike is made with `ads_create_custom_audience`; that is a write and needs approval.
   For each: location, age, gender, interests or audiences, placements, suggested daily budget and test length (at least 7 days).
5. **Special ad categories** (housing, employment, credit, social issues, elections, politics): remind the user of the targeting limits and do not narrow by age, gender or postcode.
6. **Approval**, then build:
   - Under an existing campaign, create each approved variant with `ads_create_ad_set`. Ad sets are created paused.
   - For a clean comparison, offer a split test: `ads_experiment_check_eligibility`, then `ads_experiment_abtest_create_test` with one cell per variant.
   - If there is no campaign yet, hand over to `campaign-launch`.
   - Never upload customer lists (`ads_update_custom_audience_users`) unless the user explicitly asks; it sends hashed personal data to Meta.
7. **Record**: write the new ad set and audience IDs and their settings to `reports/audience-YYYY-MM-DD.md`.
