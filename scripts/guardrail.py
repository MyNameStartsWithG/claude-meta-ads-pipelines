"""Claude Code PreToolUse hook: guardrails for Meta Ads MCP tool calls.

Runs before every mcp__meta-ads__* call and checks it against guardrails.json.
A violation denies the call with a reason Claude relays to the user. Anything
unexpected (unreadable input or config, a crash) also denies the call: a
guardrail that cannot check a call must not wave it through.
"""

import json
import os
import re
import sys
from pathlib import Path

# Tools that create campaigns, ad sets and ads. Meta creates these paused.
CREATE_TOOLS = {"ads_create_campaign", "ads_create_ad_set", "ads_create_ad"}
# Tools that put an entity live and start spending.
ACTIVATE_TOOLS = {"ads_activate_entity", "ads_boost_ig_post"}
# A tool whose name contains one of these verbs changes the account. Matching
# on the verb rather than a fixed list keeps tools Meta adds later covered.
WRITE_VERB = re.compile(
    r"(?:^|_)(?:create|update|activate|delete|boost|connect|disconnect|"
    r"publish|duplicate|copy|archive|pause|remove)(?:_|$)"
)
ACCOUNT_KEYS = {"ad_account_id", "account_id"}
STATUS_KEYS = {"status", "configured_status"}
LIMIT_KEYS = ("max_daily_budget", "max_lifetime_budget")


def short_name(tool_name):
    # "mcp__meta-ads__ads_create_campaign" -> "ads_create_campaign"
    return tool_name.rsplit("__", 1)[-1]


def is_write(tool):
    return WRITE_VERB.search(tool) is not None


def walk(value, path=""):
    """Yields (key, value, path) for every key in nested dicts and lists."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield key, child, child_path
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, f"{path}[{i}]")


def budget_limit(key):
    """Returns the guardrails.json limit that applies to a field, or None."""
    if key != "budget" and not key.endswith("_budget"):
        return None
    return "max_daily_budget" if "daily" in key else "max_lifetime_budget"


def to_number(value):
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_account(value):
    return str(value).removeprefix("act_")


def load_config(project_dir):
    with open(project_dir / "guardrails.json", encoding="utf-8") as f:
        config = json.load(f)
    for key in LIMIT_KEYS:
        if to_number(config.get(key)) is None:
            raise ValueError(f"guardrails.json: {key} must be a number")
    return config


def check(tool, tool_input, config):
    """Returns the list of violations; an empty list lets the call through."""
    problems = []
    statuses = []
    write = is_write(tool)
    allowed_accounts = {normalize_account(a) for a in config.get("allowed_ad_account_ids") or []}

    for key, value, path in walk(tool_input):
        key = key.lower()
        limit = budget_limit(key)
        if limit and not isinstance(value, (dict, list)):
            amount = to_number(value)
            if amount is None or amount > config[limit]:
                problems.append(f"{path}={value!r} is above {limit} ({config[limit]}) or not a number")
        elif key in STATUS_KEYS:
            statuses.append(str(value).upper())
        elif key in ACCOUNT_KEYS and write and allowed_accounts:
            if normalize_account(value) not in allowed_accounts:
                problems.append(f"{path}={value} is not in allowed_ad_account_ids")

    if tool in CREATE_TOOLS and config.get("require_paused_on_create", True):
        if any(s != "PAUSED" for s in statuses):
            problems.append("new campaigns, ad sets and ads must be created PAUSED")

    if tool == "ads_update_entity" and "ACTIVE" in statuses:
        problems.append("go live with ads_activate_entity, not ads_update_entity")

    if tool in ACTIVATE_TOOLS and config.get("block_activate", False):
        problems.append("going live is turned off (block_activate)")

    if write and "delete" in tool and config.get("block_delete", True):
        problems.append("deleting is turned off (block_delete)")

    return problems


def deny(reason):
    # ensure_ascii keeps stdout pure ASCII whatever the console code page is.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Guardrail: {reason} (limits live in guardrails.json)",
        }
    }))
    sys.exit(0)


def main():
    try:
        # Claude Code sends UTF-8; sys.stdin would decode with the locale code page on Windows.
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parent.parent)
        config = load_config(project_dir)
        problems = check(short_name(event["tool_name"]), event.get("tool_input") or {}, config)
    except Exception as e:
        deny(f"could not check this call ({type(e).__name__}: {e})")

    if problems:
        deny("; ".join(problems))


if __name__ == "__main__":
    main()
