import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from guardrail import check, is_write  # noqa: E402

CONFIG = {
    "max_daily_budget": 50000,
    "max_lifetime_budget": 1000000,
    "require_paused_on_create": True,
    "block_activate": False,
    "block_delete": True,
    "allowed_ad_account_ids": [],
}

# Tool inventory from Meta's Ads MCP server docs (developers.facebook.com,
# "Ads MCP Server" > tool category pages), October 2026.
READ_TOOLS = [
    "ads_get_ad_accounts", "ads_get_ad_account_pages", "ads_get_pages_for_business",
    "ads_get_user_pages", "ads_get_field_context", "ads_get_creatives", "ads_get_creative_ads",
    "ads_get_ad_images", "ads_get_ad_videos", "ads_get_ad_preview", "ads_get_ad_entities",
    "ads_library_search", "ads_get_ig_accounts", "ads_get_ig_media",
    "ads_get_ad_account_custom_audiences", "ads_get_custom_audience",
    "ads_get_custom_audience_adsets", "ads_get_opportunity_score",
    "ads_insights_advertiser_context", "ads_insights_anomaly_signal",
    "ads_insights_auction_ranking_benchmarks", "ads_insights_industry_benchmark",
    "ads_insights_performance_trend", "ads_catalog_list_catalogs",
    "ads_catalog_list_dpa_eligible_catalogs", "ads_catalog_get_diagnostics",
    "ads_catalog_get_dynamic_ads_health", "ads_catalog_get_data_sources",
    "ads_catalog_list_products", "ads_catalog_get_suggested_filter",
    "ads_catalog_list_product_sets", "ads_catalog_list_product_feeds",
    "ads_catalog_get_product_feed_upload_sessions", "ads_catalog_get_feed_rules",
    "ads_catalog_event_source_get", "ads_catalog_event_source_get_catalogs",
    "ads_catalog_event_source_get_health", "ads_catalog_event_source_get_recommendations",
    "ads_get_datasets", "ads_get_dataset_details", "ads_get_dataset_stats",
    "ads_get_dataset_quality", "ads_pixel_event_read", "ads_pixel_parameter_read",
    "ads_get_customconversions", "ads_get_errors", "ads_get_help_article",
    "ads_experiment_list_tests", "ads_experiment_check_eligibility",
    "ads_experiment_abtest_get_test", "ads_experiment_lift_get_test",
    "ads_account_get_activity_logs",
]
WRITE_TOOLS = [
    "ads_create_campaign", "ads_create_ad_set", "ads_create_ad", "ads_update_entity",
    "ads_activate_entity", "ads_create_creative", "ads_boost_ig_post",
    "ads_create_custom_audience", "ads_update_custom_audience",
    "ads_update_custom_audience_users", "ads_delete_custom_audience",
    "ads_catalog_create", "ads_catalog_update_catalog", "ads_catalog_product_create",
    "ads_catalog_update_product", "ads_catalog_delete_product",
    "ads_catalog_create_product_set", "ads_catalog_update_product_set",
    "ads_catalog_product_set_delete", "ads_catalog_create_product_feed",
    "ads_catalog_update_product_feed", "ads_catalog_create_product_feed_upload_session",
    "ads_catalog_product_feed_delete", "ads_catalog_create_feed_rule",
    "ads_catalog_product_feed_delete_rule", "ads_catalog_event_source_connect",
    "ads_catalog_event_source_disconnect", "ads_pixel_event_create",
    "ads_pixel_event_update", "ads_pixel_event_delete", "ads_pixel_parameter_create",
    "ads_pixel_parameter_update", "ads_pixel_parameter_delete",
    "ads_experiment_abtest_create_test", "ads_experiment_abtest_update_test",
    "ads_experiment_lift_create_test",
]


class ClassificationTests(unittest.TestCase):
    def test_official_read_tools_are_reads(self):
        self.assertEqual([t for t in READ_TOOLS if is_write(t)], [])

    def test_official_write_tools_are_writes(self):
        self.assertEqual([t for t in WRITE_TOOLS if not is_write(t)], [])

    def test_settings_ask_list_covers_every_write_tool(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        ask = {rule.rsplit("__", 1)[-1] for rule in settings["permissions"]["ask"]}
        self.assertEqual(sorted(set(WRITE_TOOLS) - ask), [])


class CheckTests(unittest.TestCase):
    def test_paused_campaign_within_budget_allowed(self):
        inp = {"name": "Test", "status": "PAUSED", "daily_budget": 20000}
        self.assertEqual(check("ads_create_campaign", inp, CONFIG), [])

    def test_create_without_status_allowed(self):
        # Meta creates campaigns, ad sets and ads paused by default.
        self.assertEqual(check("ads_create_ad_set", {"daily_budget": 1000}, CONFIG), [])

    def test_create_active_denied(self):
        self.assertTrue(check("ads_create_ad", {"status": "ACTIVE"}, CONFIG))

    def test_daily_budget_over_limit_denied(self):
        inp = {"status": "PAUSED", "daily_budget": "60000"}
        self.assertTrue(check("ads_create_campaign", inp, CONFIG))

    def test_nested_budget_checked(self):
        inp = {"entity_id": "1", "fields": {"daily_budget": 999999}}
        self.assertTrue(check("ads_update_entity", inp, CONFIG))

    def test_non_numeric_budget_denied(self):
        inp = {"entity_id": "1", "fields": {"daily_budget": "a lot"}}
        self.assertTrue(check("ads_update_entity", inp, CONFIG))

    def test_budget_field_names(self):
        self.assertTrue(check("ads_boost_ig_post", {"campaign_daily_budget": 60000}, CONFIG))
        self.assertEqual(check("ads_boost_ig_post", {"budget": 60000}, CONFIG), [])
        self.assertTrue(check("ads_boost_ig_post", {"budget": 2000000}, CONFIG))
        self.assertEqual(check("ads_create_campaign", {"budget_type": "DAILY"}, CONFIG), [])

    def test_unknown_write_tool_still_budget_checked(self):
        self.assertTrue(check("ads_duplicate_campaign", {"daily_budget": 90000}, CONFIG))

    def test_update_to_active_denied(self):
        inp = {"entity_id": "1", "fields": {"status": "ACTIVE"}}
        self.assertTrue(check("ads_update_entity", inp, CONFIG))

    def test_update_budget_or_pause_allowed(self):
        self.assertEqual(check("ads_update_entity", {"entity_id": "1", "daily_budget": 30000}, CONFIG), [])
        self.assertEqual(check("ads_update_entity", {"entity_id": "1", "status": "PAUSED"}, CONFIG), [])

    def test_go_live_blocked_when_configured(self):
        cfg = dict(CONFIG, block_activate=True)
        self.assertTrue(check("ads_activate_entity", {"entity_id": "1"}, cfg))
        self.assertTrue(check("ads_boost_ig_post", {"media_id": "1"}, cfg))
        self.assertEqual(check("ads_activate_entity", {"entity_id": "1"}, CONFIG), [])

    def test_delete_blocked_by_default(self):
        self.assertTrue(check("ads_delete_custom_audience", {"audience_id": "1"}, CONFIG))
        cfg = dict(CONFIG, block_delete=False)
        self.assertEqual(check("ads_delete_custom_audience", {"audience_id": "1"}, cfg), [])

    def test_account_allowlist_applies_to_writes(self):
        cfg = dict(CONFIG, allowed_ad_account_ids=["act_123"])
        self.assertEqual(check("ads_create_campaign", {"ad_account_id": "123"}, cfg), [])
        self.assertTrue(check("ads_create_campaign", {"ad_account_id": "act_999"}, cfg))
        self.assertEqual(check("ads_get_ad_entities", {"ad_account_id": "act_999"}, cfg), [])


class HookProcessTests(unittest.TestCase):
    def run_hook(self, payload, command=None, project_dir=ROOT):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project_dir))
        data = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return subprocess.run(
            command or [sys.executable, str(ROOT / "scripts" / "guardrail.py")],
            input=data, capture_output=True, env=env,
        )

    def decision(self, result):
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_read_tool_passes_silently(self):
        r = self.run_hook({"tool_name": "mcp__meta-ads__ads_get_ad_accounts", "tool_input": {}})
        self.assertEqual((r.returncode, r.stdout), (0, b""))

    def test_violation_emits_deny(self):
        r = self.run_hook({
            "tool_name": "mcp__meta-ads__ads_create_campaign",
            "tool_input": {"status": "ACTIVE", "daily_budget": 10},
        })
        self.assertEqual(self.decision(r), "deny")

    def test_non_ascii_input_is_denied_not_crashed(self):
        # The thumbs-up emoji contains byte 0x8D, which cp1252 cannot decode.
        r = self.run_hook({
            "tool_name": "mcp__meta-ads__ads_update_entity",
            "tool_input": {"entity_id": "1", "name": "Café скидка", "daily_budget": "500 \U0001F44D"},
        })
        self.assertEqual((r.returncode, self.decision(r)), (0, "deny"))

    def test_malformed_input_denied(self):
        r = self.run_hook(b"not json")
        self.assertEqual(self.decision(r), "deny")

    def test_missing_config_denied(self):
        with tempfile.TemporaryDirectory() as empty:
            r = self.run_hook({"tool_name": "mcp__meta-ads__ads_get_ad_accounts", "tool_input": {}},
                              project_dir=empty)
        self.assertEqual(self.decision(r), "deny")

    @unittest.skipUnless(shutil.which("sh"), "sh not available")
    def test_wrapper_runs_guardrail(self):
        cmd = [shutil.which("sh"), str(ROOT / "scripts" / "run-guardrail.sh")]
        ok = self.run_hook({"tool_name": "mcp__meta-ads__ads_get_ad_accounts", "tool_input": {}}, cmd)
        self.assertEqual((ok.returncode, ok.stdout), (0, b""))
        bad = self.run_hook({"tool_name": "mcp__meta-ads__ads_create_ad", "tool_input": {"status": "ACTIVE"}}, cmd)
        self.assertEqual(self.decision(bad), "deny")


if __name__ == "__main__":
    unittest.main()
