from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rank_review_queue import QueueError, build_review_queue  # noqa: E402


class ReviewQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = json.loads((ROOT / "examples" / "review-items.example.json").read_text(encoding="utf-8"))

    def test_verified_item_is_sent_to_operator(self) -> None:
        output = build_review_queue(copy.deepcopy(self.example))
        first = output["items"][0]
        self.assertEqual(first["id"], "xiaohongshu:synthetic-note-1")
        self.assertEqual(first["review_score"], 18)
        self.assertEqual(first["queue_state"], "send_to_operator")
        self.assertTrue(first["ready_for_response_drafting"])

    def test_partial_understanding_is_held(self) -> None:
        output = build_review_queue(copy.deepcopy(self.example))
        partial = next(item for item in output["items"] if item["id"].endswith("synthetic-note-2"))
        self.assertEqual(partial["queue_state"], "hold")
        self.assertFalse(partial["ready_for_response_drafting"])

    def test_unreviewed_relationship_disclosure_is_blocked(self) -> None:
        data = copy.deepcopy(self.example)
        item = data["items"][0]
        item["relationship_disclosure_required"] = True
        item["disclosure_reviewed"] = False
        output = build_review_queue(data)
        result = next(candidate for candidate in output["items"] if candidate["id"] == item["id"])
        self.assertEqual(result["queue_state"], "blocked")
        self.assertEqual(result["risk_level"], "R2")

    def test_sensitive_topic_is_blocked(self) -> None:
        data = copy.deepcopy(self.example)
        data["items"][0]["evidence"]["sensitive_topic"] = True
        output = build_review_queue(data)
        result = next(item for item in output["items"] if item["id"].endswith("synthetic-note-1"))
        self.assertEqual(result["queue_state"], "blocked")
        self.assertEqual(result["risk_level"], "R3")

    def test_zero_voice_samples_require_low_confidence(self) -> None:
        data = copy.deepcopy(self.example)
        data["voice_context"].update(
            {
                "source": "insufficient_public_evidence",
                "profile_reads": 0,
                "posts_sampled": 0,
                "confidence": "medium",
                "patterns": [],
                "source_ids": [],
            }
        )
        with self.assertRaisesRegex(QueueError, "low voice confidence"):
            build_review_queue(data)

    def test_zero_voice_samples_are_accepted_when_explicit(self) -> None:
        data = copy.deepcopy(self.example)
        data["voice_context"].update(
            {
                "source": "insufficient_public_evidence",
                "profile_reads": 0,
                "posts_sampled": 0,
                "confidence": "low",
                "patterns": [],
                "source_ids": [],
            }
        )
        output = build_review_queue(data)
        self.assertEqual(output["items"][0]["queue_state"], "send_to_operator")

    def test_target_mismatch_is_blocked(self) -> None:
        data = copy.deepcopy(self.example)
        data["items"][0]["evidence"]["target_matched"] = False
        output = build_review_queue(data)
        result = next(item for item in output["items"] if item["id"].endswith("synthetic-note-1"))
        self.assertEqual(result["queue_state"], "blocked")
        self.assertEqual(result["risk_level"], "R3")

    def test_duplicate_ids_are_rejected(self) -> None:
        data = copy.deepcopy(self.example)
        data["items"][1]["id"] = data["items"][0]["id"]
        with self.assertRaisesRegex(QueueError, "unique"):
            build_review_queue(data)


if __name__ == "__main__":
    unittest.main()
