"""Claude Code PreToolUse hook: Meta Ads MCP yazma araçları için güvenlik bariyeri.

Okuma araçlarına dokunmaz. Yazma araçlarında guardrails.json'daki sınırları
kontrol eder; sınır aşılırsa çağrıyı reddeder (Claude'a gerekçesiyle döner).
Yapılandırma okunamazsa yazma çağrıları reddedilir (fail-closed).
"""

import json
import os
import sys
from pathlib import Path

CREATE_TOOLS = {"ads_create_campaign", "ads_create_ad_set", "ads_create_ad"}
WRITE_TOOLS = CREATE_TOOLS | {
    "ads_update_entity",
    "ads_activate_entity",
    "ads_catalog_create",
}
ACCOUNT_KEYS = {"ad_account_id", "account_id"}


def short_name(tool_name):
    # "mcp__meta-ads__ads_create_campaign" -> "ads_create_campaign"
    return tool_name.rsplit("__", 1)[-1]


def walk(value, path=""):
    """Sözlük/listeyi gezip (anahtar, değer, yol) üçlülerini üretir."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield key, child, child_path
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, f"{path}[{i}]")


def to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_account(value):
    return str(value).removeprefix("act_")


def load_config(project_dir):
    with open(project_dir / "guardrails.json", encoding="utf-8") as f:
        return json.load(f)


def check(tool, tool_input, config):
    """İhlalleri liste olarak döner; boş liste = izin."""
    problems = []
    statuses = []

    for key, value, path in walk(tool_input):
        key_l = key.lower()
        if key_l == "daily_budget":
            amount = to_number(value)
            if amount is None or amount > config["max_daily_budget"]:
                problems.append(
                    f"{path}={value} günlük bütçe sınırını "
                    f"({config['max_daily_budget']}) aşıyor veya sayı değil"
                )
        elif key_l == "lifetime_budget":
            amount = to_number(value)
            if amount is None or amount > config["max_lifetime_budget"]:
                problems.append(
                    f"{path}={value} toplam bütçe sınırını "
                    f"({config['max_lifetime_budget']}) aşıyor veya sayı değil"
                )
        elif key_l in ("status", "configured_status"):
            statuses.append(str(value).upper())
        elif key_l in ACCOUNT_KEYS and config.get("allowed_ad_account_ids"):
            allowed = {normalize_account(a) for a in config["allowed_ad_account_ids"]}
            if normalize_account(value) not in allowed:
                problems.append(f"{path}={value} izinli reklam hesapları listesinde değil")

    if tool in CREATE_TOOLS and config.get("require_paused_on_create", True):
        if not statuses or any(s != "PAUSED" for s in statuses):
            problems.append("yeni kayıtlar status=PAUSED ile oluşturulmalı")

    if tool == "ads_update_entity" and "ACTIVE" in statuses:
        problems.append("yayına alma ads_update_entity ile değil ads_activate_entity ile yapılmalı")

    if tool == "ads_activate_entity" and config.get("block_activate", False):
        problems.append("guardrails.json: block_activate=true, yayına alma kapalı")

    return problems


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Guardrail: {reason}",
        }
    }, ensure_ascii=False))
    sys.exit(0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        deny("hook girdisi okunamadı")

    tool = short_name(event.get("tool_name", ""))
    if tool not in WRITE_TOOLS:
        sys.exit(0)

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parent.parent)
    try:
        config = load_config(project_dir)
    except (OSError, json.JSONDecodeError, KeyError) as e:
        deny(f"guardrails.json okunamadı ({e}); yazma işlemleri kapalı")

    try:
        problems = check(tool, event.get("tool_input") or {}, config)
    except KeyError as e:
        deny(f"guardrails.json eksik alan: {e}")

    if problems:
        deny("; ".join(problems))
    sys.exit(0)


if __name__ == "__main__":
    main()
