import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from guardrail import check  # noqa: E402

CONFIG = {
    "max_daily_budget": 50000,
    "max_lifetime_budget": 1000000,
    "require_paused_on_create": True,
    "block_activate": False,
    "allowed_ad_account_ids": [],
}


class CheckTests(unittest.TestCase):
    def test_paused_campaign_within_budget_allowed(self):
        inp = {"name": "Test", "status": "PAUSED", "daily_budget": 20000}
        self.assertEqual(check("ads_create_campaign", inp, CONFIG), [])

    def test_create_without_status_denied(self):
        self.assertTrue(check("ads_create_ad_set", {"daily_budget": 1000}, CONFIG))

    def test_create_active_denied(self):
        self.assertTrue(check("ads_create_ad", {"status": "ACTIVE"}, CONFIG))

    def test_daily_budget_over_limit_denied(self):
        inp = {"status": "PAUSED", "daily_budget": "60000"}
        self.assertTrue(check("ads_create_campaign", inp, CONFIG))

    def test_nested_budget_checked(self):
        inp = {"entity_id": "1", "fields": {"daily_budget": 999999}}
        self.assertTrue(check("ads_update_entity", inp, CONFIG))

    def test_non_numeric_budget_denied(self):
        inp = {"entity_id": "1", "fields": {"daily_budget": "çok"}}
        self.assertTrue(check("ads_update_entity", inp, CONFIG))

    def test_update_to_active_denied(self):
        inp = {"entity_id": "1", "fields": {"status": "ACTIVE"}}
        self.assertTrue(check("ads_update_entity", inp, CONFIG))

    def test_update_budget_within_limit_allowed(self):
        inp = {"entity_id": "1", "fields": {"daily_budget": 30000}}
        self.assertEqual(check("ads_update_entity", inp, CONFIG), [])

    def test_activate_blocked_when_configured(self):
        cfg = dict(CONFIG, block_activate=True)
        self.assertTrue(check("ads_activate_entity", {"entity_id": "1"}, cfg))
        self.assertEqual(check("ads_activate_entity", {"entity_id": "1"}, CONFIG), [])

    def test_account_allowlist(self):
        cfg = dict(CONFIG, allowed_ad_account_ids=["act_123"])
        ok = {"ad_account_id": "123", "status": "PAUSED"}
        bad = {"ad_account_id": "act_999", "status": "PAUSED"}
        self.assertEqual(check("ads_create_campaign", ok, cfg), [])
        self.assertTrue(check("ads_create_campaign", bad, cfg))


class HookProcessTests(unittest.TestCase):
    def run_hook(self, event):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "guardrail.py")],
            input=json.dumps(event), capture_output=True, text=True,
            encoding="utf-8", env=env,
        )

    def test_read_tool_passes_silently(self):
        r = self.run_hook({"tool_name": "mcp__meta-ads__ads_get_ad_accounts", "tool_input": {}})
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_write_violation_emits_deny(self):
        r = self.run_hook({
            "tool_name": "mcp__meta-ads__ads_create_campaign",
            "tool_input": {"status": "ACTIVE", "daily_budget": 10},
        })
        out = json.loads(r.stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
