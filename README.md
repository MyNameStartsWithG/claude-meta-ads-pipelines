# Meta Ads pipelines for Claude Code and Codex

Connect Claude Code (or Codex) to Meta's official **Ads MCP server** and run your ad account like a small in-house team: audits, tracking checks, budget moves, audiences and campaign launches. Anything that spends money waits for your approval and has to pass a guardrail that runs as code, not as a prompt.

```
┌──────────────┐   OAuth (Facebook login)  ┌──────────────────────────────┐
│ Claude Code  │ ────────────────────────▶ │ Meta Ads MCP server          │
│   / Codex    │ ◀──────────────────────── │ https://mcp.facebook.com/ads │
└──────┬───────┘                           └──────────────────────────────┘
       │
       ├─ .claude/skills/   5 pipelines (step-by-step playbooks)
       ├─ .claude/agents/   read-only analyst subagent
       └─ PreToolUse hook   scripts/guardrail.py: budget caps, paused-only creation, no deletes
```

## Pipelines

| Command | What it does | Changes the account |
|---|---|---|
| `/ads-audit` | KPI trends, anomalies, delivery errors, recent changes, industry benchmarks → `reports/audit-*.md` | No |
| `/tracking-health` | Pixel / Conversions API volumes, Event Match Quality, event rules, catalog diagnostics | No |
| `/budget-optimizer` | Scale / hold / cut / pause plan; ±20% steps, total spend kept flat | After approval |
| `/audience-builder` | Three audience variants (broad, interests, warm or lookalike) → paused ad sets, optional A/B test | After approval |
| `/campaign-launch` | Brief → competitor scan → creative → campaign → ad sets → ads, all paused; preview, then go live on a separate yes | After approval |

Plain language works too: *"audit the last 7 days"*, *"move budget to the campaigns that are winning"*.

## Requirements

- [Claude Code](https://code.claude.com) **2.1.295 or later** (the guardrail relies on the hook's `onFailure: "block"` setting), or the Codex CLI
- Python 3.9+ and `sh`: built in on macOS and Linux; on Windows, Git Bash, which Claude Code uses
- A Meta account with access to the ad accounts you want to manage. The server acts with that user's rights.

## Setup

### Claude Code

```bash
git clone https://github.com/MyNameStartsWithG/claude-meta-ads-pipelines.git
cd claude-meta-ads-pipelines
claude
```

1. **Trust the folder** when Claude Code asks, and approve the `meta-ads` server from `.mcp.json`. Until the folder is trusted, Claude Code ignores the project's allow rules: even read-only calls will prompt, and headless runs are refused.
2. Run `/mcp`, pick `meta-ads` → **Authenticate**. Log in with Facebook and choose which ad accounts and Pages to share.
3. Start with `/ads-audit`.

**Using your own Meta app** (optional, for example when your business manages agent access through its own app): create an app at developers.facebook.com, add the *Create & manage ads with ads MCP server* use case, and register `http://localhost:8765/callback` as a redirect URL under Facebook Login for Business. Then:

```bash
claude mcp add --transport http --client-id <META_APP_ID> --callback-port 8765 meta-ads https://mcp.facebook.com/ads
```

Keep the server name `meta-ads`: the permission rules and the guardrail match on it.

### Codex

```bash
codex mcp add meta-ads --url https://mcp.facebook.com/ads
codex mcp login meta-ads
codex
```

Codex reads `AGENTS.md`, which sends it to the same pipeline files. Codex does not run Claude Code hooks, so there the guardrail is applied by instruction only; see `AGENTS.md`.

### Claude.ai and Claude Desktop

Settings → Connectors → *Add custom connector* → `https://mcp.facebook.com/ads`. The connector works there, but the permission rules and the guardrail in this repository only apply in Claude Code.

## Safety

Four layers, from Meta's side to the prompt:

| Layer | Where | What it does |
|---|---|---|
| Meta | Business settings | Ads MCP server rules let a business portfolio admin with full control limit what agents may do, from budget changes to catalog updates. Account and campaign spending limits cap spend. At login, share only the ad accounts you need; start with read-only access (`ads_read`). |
| Permissions | `.claude/settings.json` | Read tools run without prompts. All 36 write tools ask every time. |
| Guardrail | `scripts/guardrail.py` + `guardrails.json` | Runs before every `meta-ads` call, ahead of any permission rule or prompt, and denies the call if it breaks a limit (below). |
| Pipelines | `.claude/skills/`, `CLAUDE.md` | Plan table and explicit approval before any write, ±20% budget steps, a separate yes before going live, no invented numbers or targeting IDs. |

The guardrail denies a call when:

- any budget field (`daily_budget`, `lifetime_budget`, `budget` or anything ending in `_budget`, nested or not) is above its limit or not a number
- a campaign, ad set or ad is created with a status other than `PAUSED` (Meta creates them paused by default)
- `ads_update_entity` tries to set `ACTIVE`; going live goes through `ads_activate_entity`, which always asks
- `block_activate` is on and the call would go live (`ads_activate_entity`, `ads_boost_ig_post`)
- `block_delete` is on (the default) and the tool deletes something
- `allowed_ad_account_ids` is set and a write targets another account

Write tools are recognised by their verb (`create`, `update`, `delete`, `boost`, ...), so tools Meta adds later are still checked. The guardrail fails closed: if Python is missing, the script crashes or it times out, the call is blocked.

### Configuration

`guardrails.json`. Amounts are in the account currency's minor unit (cents), as Meta's Marketing API expects: `50000` = 500.00.

| Key | Default | Meaning |
|---|---|---|
| `max_daily_budget` | `50000` | Highest daily budget any call may set |
| `max_lifetime_budget` | `1000000` | Highest lifetime budget any call may set |
| `require_paused_on_create` | `true` | New campaigns, ad sets and ads may not be created live |
| `block_activate` | `false` | `true` turns off going live and boosting completely |
| `block_delete` | `true` | Deny every delete tool |
| `allowed_ad_account_ids` | `[]` | If set (e.g. `["act_1234567890"]`), writes to any other account are denied |

## Running headless

Once the folder is trusted and you have logged in, the read-only pipelines run without prompts, for example from a scheduled job:

```bash
claude -p "/ads-audit last 7 days"
```

Write tools need approval, so in `-p` mode they are refused rather than run.

## Project layout

```
.mcp.json                  Meta Ads MCP server for Claude Code
.claude/settings.json      permissions and the guardrail hook
.claude/skills/            the five pipelines
.claude/agents/            ads-analyst, read-only subagent
CLAUDE.md, AGENTS.md       rules for Claude Code and Codex
guardrails.json            limits
scripts/guardrail.py       the hook
scripts/run-guardrail.sh   finds a working Python, blocks the call if there is none
tests/                     guardrail tests
reports/                   pipeline output (not committed)
```

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover every guardrail rule, non-ASCII input (emoji and Cyrillic in ad copy), malformed input, a missing config, and the read/write split of every tool in Meta's published inventory. They also check that the `ask` list in `.claude/settings.json` covers every known write tool. CI runs them on Ubuntu and Windows.

## Notes

- Tool names follow Meta's [Ads MCP server documentation](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-overview) as of October 2026. Meta is still adding tools. The guardrail catches new write tools by verb; add them to the `ask` list as well, and the tests will tell you if the list falls behind the inventory in `tests/test_guardrail.py`.
- The MCP server has no image upload. Creatives use images and videos already in the ad account.
- This project is not affiliated with Meta. You are responsible for the changes made to your ad accounts.

## License

MIT
