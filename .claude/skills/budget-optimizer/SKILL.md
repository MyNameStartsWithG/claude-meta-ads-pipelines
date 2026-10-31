---
name: budget-optimizer
description: Reallocates budget across Meta campaigns and ad sets by performance. Builds a scale / hold / cut / pause plan, and applies it with ads_update_entity only after the user approves. Use for "optimize my budget", "move budget to the winners", "cut the losing campaigns", /budget-optimizer.
---

# Pipeline 3: Budget optimization (plan first, apply on approval)

## Rules
- Change any single budget by **at most 20%** per run, so the delivery system does not re-enter learning.
- Leave ad sets that are still learning (under about 50 optimization events in the last 7 days) alone; mark them "learning" in the plan.
- Leave anything whose budget was edited in the last 3 days alone (check the activity log).
- Keep total daily spend **flat** unless the user says otherwise: what you take from losers goes to winners.
- Budgets are sent in the account currency's minor unit (cents): 50000 = 500.00. The guardrail hook rejects anything above the limits in `guardrails.json`; do not try to work around a rejection, tell the user.
- Going live (ACTIVE) is not part of this pipeline.

## Steps
1. **Data**: `ads_get_ad_entities` for the last 7 and 14 days. Note whether each campaign uses campaign budget (Advantage+ campaign budget) or ad set budgets; change the budget where it lives.
2. **Recent edits**: `ads_account_get_activity_logs` for the last 3 days.
3. **Targets**: ask for the target CPA or ROAS if you do not have it. Do not silently fall back to the account average.
4. **Classify** each budget holder:
   - **Scale**: CPA at or below 80% of target, or ROAS at or above 120% of target → +10–20%
   - **Hold**: within ±20% of target
   - **Cut**: CPA at 120–200% of target → −10–20%
   - **Pause (proposal)**: CPA above 2× target, or spend of 2× target CPA with no results
5. **Plan table**: unit, current budget, new budget, change %, reason; plus total daily spend before and after, in the account currency.
6. **Approval**: wait for an explicit "apply" (or a list of row numbers). Without it, stop here.
7. **Apply**: `ads_update_entity` for each approved row. Pausing means `status: PAUSED`.
8. **Verify**: read the changed entities back with `ads_get_ad_entities` and compare with the plan.
9. **Record**: write `reports/budget-YYYY-MM-DD.md` with the plan, what was applied, and anything the guardrail denied.
