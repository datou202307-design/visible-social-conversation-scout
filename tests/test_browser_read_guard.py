from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from authorize_browser_read import GateError, authorize_browser_read  # noqa: E402


class BrowserReadGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads((ROOT / "examples" / "run-plan.example.json").read_text(encoding="utf-8"))

    def build_inputs(self) -> tuple[bytes, dict[str, str]]:
        raw = (json.dumps(self.plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        receipt = {
            "schema_version": "visible-conversation-run-v1",
            "platform": "xiaohongshu",
            "access_route": "visible_browser",
            "status": "accepted",
            "input_sha256": hashlib.sha256(raw).hexdigest(),
        }
        return raw, receipt

    def test_matching_receipt_authorizes_platform_root(self) -> None:
        raw, receipt = self.build_inputs()
        result = authorize_browser_read(raw, receipt, "https://www.xiaohongshu.com/")
        self.assertEqual(result["status"], "authorized")
        self.assertEqual(result["platform"], "xiaohongshu")

    def test_modified_plan_is_rejected(self) -> None:
        raw, receipt = self.build_inputs()
        modified = json.loads(raw.decode("utf-8"))
        modified["subject"] = "changed after receipt"
        modified_raw = (json.dumps(modified, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        with self.assertRaisesRegex(GateError, "digest does not match"):
            authorize_browser_read(modified_raw, receipt, "https://www.xiaohongshu.com/")

    def test_unaccepted_receipt_is_rejected(self) -> None:
        raw, receipt = self.build_inputs()
        rejected = copy.deepcopy(receipt)
        rejected["status"] = "rejected"
        with self.assertRaisesRegex(GateError, "status must be accepted"):
            authorize_browser_read(raw, rejected, "https://www.xiaohongshu.com/")

    def test_cross_platform_target_is_rejected(self) -> None:
        raw, receipt = self.build_inputs()
        with self.assertRaisesRegex(GateError, "host does not match"):
            authorize_browser_read(raw, receipt, "https://www.douyin.com/")

    def test_signed_or_parameterized_first_url_is_rejected(self) -> None:
        raw, receipt = self.build_inputs()
        with self.assertRaisesRegex(GateError, "query parameters"):
            authorize_browser_read(raw, receipt, "https://www.xiaohongshu.com/?token=synthetic")


if __name__ == "__main__":
    unittest.main()
