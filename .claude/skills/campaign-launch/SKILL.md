---
name: campaign-launch
description: End-to-end Meta campaign setup from a brief - competitor scan, creative, campaign, ad sets and ads, all created paused, with a preview before anything goes live on a separate approval. Use for "launch a campaign", "set up a new ad", "prepare a launch campaign", /campaign-launch.
---

# Pipeline 5: Campaign launch

Everything is created **paused**. Going live is a separate step with its own approval.

## 1. Brief (ask for what is missing; do not guess)
- Ad account and Facebook Page (`ads_get_ad_accounts`, `ads_get_ad_account_pages` or `ads_get_user_pages`); Instagram account if needed (`ads_get_ig_accounts`)
- Objective: awareness, traffic, engagement, leads, app promotion or sales
- Daily or lifetime budget, start and end dates
- Audience (if there is none, run `audience-builder`)
- Creative: image or video, primary text, headline, call to action, destination URL
- For conversion objectives: which dataset and event; run `tracking-health` first if unsure

## 2. Research (optional, quick)
`ads_library_search` for 3–5 active competitor ads in the same category: note angles, offers and formats. Do not copy their copy.

## 3. Creative
- The MCP server has no image upload. Use media already in the ad account (`ads_get_ad_images`, `ads_get_ad_videos`, existing `ads_get_creatives`). If the user's image is not there yet, ask them to upload it in Ads Manager first.
- Offer 3 headlines and 3 primary texts. Avoid policy risks: guaranteed results, before/after claims, copy that asserts personal attributes ("Are you overweight?").
- Create the creative with `ads_create_creative` after approval.

## 4. Plan
Show the structure as a table:
`Campaign (objective, budget type) → Ad set(s) (audience, placements, budget, schedule) → Ad(s) (creative, text, CTA, URL)`
Naming: `YYYYMM_Objective_Product_Audience` (for example `202611_Sales_WinterCollection_Broad`).
Budgets are in the account currency's minor unit (cents); show them to the user in normal currency as well.

## 5. Build (after approval)
1. `ads_create_campaign`
2. `ads_create_ad_set` for each audience
3. `ads_create_ad` for each ad, using the creative from step 3

Do not pass `status: ACTIVE` anywhere; the guardrail denies it. If a step fails, stop, list what was created so far, and tell the user what is left half-built.

## 6. Preview
`ads_get_ad_preview` for each ad in its main placements (Feed, Stories, Reels). Show the previews and the IDs.

## 7. Go live
Ask **separately**: "Shall I make it live?" Only on an explicit yes, call `ads_activate_entity` for the campaign, then the ad sets, then the ads. Then run `ads_get_errors` to catch anything blocking delivery.

## 8. Record
Write `reports/campaign-YYYY-MM-DD-<name>.md`: brief, structure, IDs, status.
