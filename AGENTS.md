# Meta Ads pipelines: instructions for Codex

This repository works with both Claude Code and Codex. In Codex, the Meta Ads MCP server is added with `codex mcp add meta-ads --url https://mcp.facebook.com/ads` and authenticated with `codex mcp login meta-ads`.

When the user asks for one of these jobs, read the matching file and follow its steps exactly:

| Request | File |
|---|---|
| Ads analysis, report, "how are my ads doing" | `.claude/skills/ads-audit/SKILL.md` |
| Pixel, Conversions API or catalog check | `.claude/skills/tracking-health/SKILL.md` |
| Budget optimization | `.claude/skills/budget-optimizer/SKILL.md` |
| Audiences | `.claude/skills/audience-builder/SKILL.md` |
| Campaign setup | `.claude/skills/campaign-launch/SKILL.md` |

The rules in the "Rules that always apply" section of `CLAUDE.md` apply to Codex as well.

Codex does not run the Claude Code guardrail hook, so check every write yourself before calling it. Pipe the call to the guardrail script:

```
echo '{"tool_name": "ads_create_campaign", "tool_input": {"name": "...", "daily_budget": 20000}}' | python scripts/guardrail.py
```

No output means the call is within limits. Output containing `"deny"` means do not make the call; tell the user the reason it gives.
