from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_run_plan import PlanError, validate_run_plan  # noqa: E402


class RunPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = json.loads((ROOT / "examples" / "run-plan.example.json").read_text(encoding="utf-8"))

    def test_valid_example_is_accepted(self) -> None:
        receipt = validate_run_plan(copy.deepcopy(self.example))
        self.assertEqual(receipt["status"], "accepted")
        self.assertEqual(receipt["platform"], "xiaohongshu")

    def test_platform_write_is_rejected(self) -> None:
        plan = copy.deepcopy(self.example)
        plan["permissions"]["comment"] = True
        with self.assertRaisesRegex(PlanError, "permissions.comment must be false"):
            validate_run_plan(plan)

    def test_jitter_is_rejected(self) -> None:
        plan = copy.deepcopy(self.example)
        plan["cadence"]["jitter"] = True
        with self.assertRaisesRegex(PlanError, "cadence.jitter must be false"):
            validate_run_plan(plan)

    def test_short_page_wait_is_rejected(self) -> None:
        plan = copy.deepcopy(self.example)
        plan["cadence"]["page_wait_seconds"] = 19
        with self.assertRaisesRegex(PlanError, "page_wait_seconds"):
            validate_run_plan(plan)

    def test_missing_stop_is_rejected(self) -> None:
        plan = copy.deepcopy(self.example)
        plan["stop_conditions"].remove("platform_warning")
        with self.assertRaisesRegex(PlanError, "missing stop conditions"):
            validate_run_plan(plan)

    def test_delivery_below_three_is_rejected(self) -> None:
        plan = copy.deepcopy(self.example)
        plan["delivery"]["minimum_pages"] = 2
        with self.assertRaisesRegex(PlanError, "delivery.minimum_pages"):
            validate_run_plan(plan)


if __name__ == "__main__":
    unittest.main()

