# Meta Ads pipelines

This repository runs a Meta ad account through Meta's official Ads MCP server (`meta-ads`, https://mcp.facebook.com/ads). Reply in the language the user writes in.

## Pipelines (`.claude/skills/`)
| Skill | Job | Writes? |
|---|---|---|
| `ads-audit` | Performance audit and report | No |
| `tracking-health` | Pixel / Conversions API and catalog health | No |
| `budget-optimizer` | Budget reallocation | After approval |
| `audience-builder` | Audience design and paused ad sets | After approval |
| `campaign-launch` | Creative → campaign → ad sets → ads | After approval |

For read-only work across several accounts or long periods, use the `ads-analyst` subagent.

## Rules that always apply
1. These calls spend real money. Before any write, show what will change as a table and get an explicit yes.
2. New campaigns, ad sets and ads are created paused. Going live happens only through `ads_activate_entity`, after its own yes.
3. Budgets are sent in the account currency's minor unit (cents). Before sending, confirm the amount with the user in normal currency.
4. The `scripts/guardrail.py` hook enforces `guardrails.json`. If it denies a call, do not look for a way around it; tell the user why.
5. Never invent numbers or targeting IDs. Data that did not come from a tool is "no data".
6. Reports go under `reports/`, which git ignores.

## Development
Guardrail tests: `python -m unittest discover -s tests`
