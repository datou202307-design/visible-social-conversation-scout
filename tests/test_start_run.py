from __future__ import annotations

import json
import shutil
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_run_plan import PlanError  # noqa: E402
from start_run import ARTIFACT_NAMES, StartRunError, prepare_run  # noqa: E402


class StartRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_root = ROOT / ".runtime" / "test-temp"
        cls.temp_root.mkdir(parents=True, exist_ok=True)

    def setUp(self) -> None:
        self.created_paths: list[Path] = []

    def tearDown(self) -> None:
        for path in self.created_paths:
            shutil.rmtree(path, ignore_errors=True)

    def new_output_dir(self) -> Path:
        path = self.temp_root / f"run-{uuid.uuid4().hex}"
        self.created_paths.append(path)
        return path

    def options(self) -> dict[str, object]:
        return {
            "platform": "xiaohongshu",
            "subject": "synthetic example topic",
            "rule_reviewed_at": "2026-09-20",
            "operator_confirmed": True,
            "human_login_complete": True,
        }

    def test_prepares_plan_receipt_and_authorization(self) -> None:
        output_dir = self.new_output_dir()
        authorization = prepare_run(output_dir, **self.options())
        self.assertEqual(authorization["status"], "authorized")
        self.assertEqual({path.name for path in output_dir.iterdir()}, set(ARTIFACT_NAMES))

        plan = json.loads((output_dir / "run-plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["delivery"]["minimum_pages"], 3)
        self.assertEqual(plan["delivery"]["goal_pages"], 5)
        self.assertEqual(plan["delivery"]["responses_per_page"], 3)
        self.assertTrue(all(value is False for value in plan["permissions"].values()))

    def test_requires_operator_confirmation_and_human_login(self) -> None:
        options = self.options()
        options["operator_confirmed"] = False
        with self.assertRaisesRegex(StartRunError, "account owner"):
            prepare_run(self.new_output_dir(), **options)

        options["operator_confirmed"] = True
        options["human_login_complete"] = False
        with self.assertRaisesRegex(StartRunError, "complete login"):
            prepare_run(self.new_output_dir(), **options)

    def test_refuses_to_overwrite_an_existing_run(self) -> None:
        output_dir = self.new_output_dir()
        prepare_run(output_dir, **self.options())
        with self.assertRaisesRegex(StartRunError, "never overwritten"):
            prepare_run(output_dir, **self.options())

    def test_unsafe_delivery_override_is_rejected(self) -> None:
        with self.assertRaisesRegex(PlanError, "delivery.minimum_pages"):
            prepare_run(self.new_output_dir(), minimum_pages=2, **self.options())


if __name__ == "__main__":
    unittest.main()
