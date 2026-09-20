#!/usr/bin/env python3
"""Validate public conversation items and order them for human review."""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = "social-review-queue-v1"
PLATFORMS = {"douyin", "xiaohongshu"}
UNDERSTANDING_STATES = {"list_only", "partial", "verified_page", "human_reviewed"}
VOICE_SOURCES = {"current_account_public_posts", "insufficient_public_evidence"}
VOICE_CONFIDENCE = {"low", "medium", "high"}
OBSERVATION_RANGES = {
    "subject_overlap": (0, 4),
    "contribution_specificity": (0, 4),
    "audience_continuity": (0, 3),
    "attention_evidence": (0, 3),
    "response_space": (0, 3),
    "evidence_strength": (0, 5),
}
PENALTY_RANGES = {"saturation": (0, 3), "uncertainty": (0, 5)}
STATE_ORDER = {"send_to_operator": 0, "watchlist": 1, "hold": 2, "blocked": 3}


class QueueError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QueueError(message)


def require_bool(value: Any, path: str) -> bool:
    require(type(value) is bool, f"{path} must be a boolean")
    return value


def require_int(value: Any, path: str, minimum: int, maximum: int) -> int:
    require(type(value) is int, f"{path} must be an integer")
    require(minimum <= value <= maximum, f"{path} must be between {minimum} and {maximum}")
    return value


def require_object(value: Any, path: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{path} must be an object")
    return value


def validate_url(value: Any, path: str) -> str:
    require(isinstance(value, str), f"{path} must be a string")
    parsed = urlparse(value)
    require(parsed.scheme in {"http", "https"} and parsed.netloc, f"{path} must be an HTTP(S) URL")
    return value


def validate_voice_context(value: Any) -> dict[str, Any]:
    voice = require_object(value, "voice_context")
    require(voice.get("source") in VOICE_SOURCES, "voice_context.source is unsupported")
    profile_reads = require_int(voice.get("profile_reads"), "voice_context.profile_reads", 0, 1)
    posts_sampled = require_int(voice.get("posts_sampled"), "voice_context.posts_sampled", 0, 5)
    confidence = voice.get("confidence")
    require(confidence in VOICE_CONFIDENCE, "voice_context.confidence is unsupported")
    require(isinstance(voice.get("patterns"), list), "voice_context.patterns must be a list")
    require(all(isinstance(item, str) for item in voice["patterns"]), "voice_context.patterns must contain strings")
    source_ids = voice.get("source_ids")
    require(isinstance(source_ids, list) and len(source_ids) <= 5, "voice_context.source_ids must have at most five items")
    require(all(isinstance(item, str) for item in source_ids), "voice_context.source_ids must contain strings")
    require(len(source_ids) == posts_sampled, "voice_context.source_ids must match posts_sampled")
    if posts_sampled == 0:
        require(confidence == "low", "zero public post samples require low voice confidence")
        require(not voice["patterns"], "zero public post samples require an empty pattern list")
        require(
            voice.get("source") == "insufficient_public_evidence",
            "zero public post samples require insufficient_public_evidence",
        )
    else:
        require(profile_reads == 1, "public post samples require one current-account profile read")
    if profile_reads == 0:
        require(voice.get("source") == "insufficient_public_evidence", "missing profile evidence must be explicit")
    return voice


def classify_item(item: dict[str, Any], index: int) -> dict[str, Any]:
    prefix = f"items[{index}]"
    result = deepcopy(item)
    require(isinstance(item.get("id"), str) and item["id"].strip(), f"{prefix}.id is required")
    require(isinstance(item.get("content_id"), str) and item["content_id"].strip(), f"{prefix}.content_id is required")
    validate_url(item.get("source_url"), f"{prefix}.source_url")
    require(
        isinstance(item.get("public_author_label"), str) and item["public_author_label"].strip(),
        f"{prefix}.public_author_label is required",
    )
    require(isinstance(item.get("title"), str) and item["title"].strip(), f"{prefix}.title is required")

    evidence = require_object(item.get("evidence"), f"{prefix}.evidence")
    target_matched = require_bool(evidence.get("target_matched"), f"{prefix}.evidence.target_matched")
    understanding = evidence.get("understanding")
    require(understanding in UNDERSTANDING_STATES, f"{prefix}.evidence.understanding is unsupported")
    sensitive_topic = require_bool(evidence.get("sensitive_topic"), f"{prefix}.evidence.sensitive_topic")
    require(
        isinstance(evidence.get("public_excerpt"), str) and evidence["public_excerpt"].strip(),
        f"{prefix}.evidence.public_excerpt is required",
    )

    counters = require_object(item.get("public_counters"), f"{prefix}.public_counters")
    for key, value in counters.items():
        require(value is None or (type(value) is int and value >= 0), f"{prefix}.public_counters.{key} must be null or non-negative")

    observations = require_object(item.get("observations"), f"{prefix}.observations")
    observation_values: dict[str, int] = {}
    for key, (minimum, maximum) in OBSERVATION_RANGES.items():
        observation_values[key] = require_int(observations.get(key), f"{prefix}.observations.{key}", minimum, maximum)

    penalties = require_object(item.get("penalties"), f"{prefix}.penalties")
    penalty_values: dict[str, int] = {}
    for key, (minimum, maximum) in PENALTY_RANGES.items():
        penalty_values[key] = require_int(penalties.get(key), f"{prefix}.penalties.{key}", minimum, maximum)

    relationship_required = require_bool(
        item.get("relationship_disclosure_required"), f"{prefix}.relationship_disclosure_required"
    )
    disclosure_reviewed = require_bool(item.get("disclosure_reviewed"), f"{prefix}.disclosure_reviewed")
    limitations = item.get("limitations")
    require(isinstance(limitations, list) and all(isinstance(value, str) for value in limitations), f"{prefix}.limitations must be strings")

    review_score = max(0, sum(observation_values.values()) - sum(penalty_values.values()))
    strong_evidence = understanding in {"verified_page", "human_reviewed"}

    if sensitive_topic or not target_matched or (relationship_required and not disclosure_reviewed):
        queue_state = "blocked"
    elif not strong_evidence:
        queue_state = "hold"
    elif (
        review_score >= 14
        and observation_values["subject_overlap"] >= 2
        and observation_values["contribution_specificity"] >= 2
        and observation_values["evidence_strength"] >= 4
    ):
        queue_state = "send_to_operator"
    elif review_score >= 9:
        queue_state = "watchlist"
    else:
        queue_state = "hold"

    if sensitive_topic or not target_matched:
        risk_level = "R3"
    elif relationship_required:
        risk_level = "R2"
    elif queue_state == "send_to_operator":
        risk_level = "R1"
    else:
        risk_level = "R0"

    result["review_score"] = review_score
    result["queue_state"] = queue_state
    result["ready_for_response_drafting"] = queue_state == "send_to_operator"
    result["risk_level"] = risk_level
    return result


def build_review_queue(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("schema_version") == SCHEMA_VERSION, f"schema_version must be {SCHEMA_VERSION}")
    platform = data.get("platform")
    require(platform in PLATFORMS, "platform must be douyin or xiaohongshu")
    require(isinstance(data.get("captured_at"), str) and data["captured_at"].strip(), "captured_at is required")
    require(isinstance(data.get("subject"), str) and data["subject"].strip(), "subject is required")

    receipt = require_object(data.get("run_plan_receipt"), "run_plan_receipt")
    require(receipt.get("status") == "accepted", "run_plan_receipt.status must be accepted")
    digest = receipt.get("input_sha256")
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest) is not None, "run_plan_receipt.input_sha256 is invalid")
    validate_voice_context(data.get("voice_context"))

    items = data.get("items")
    require(isinstance(items, list) and items, "items must be a non-empty list")
    classified = [classify_item(item, index) for index, item in enumerate(items)]
    ids = [item["id"] for item in classified]
    require(len(ids) == len(set(ids)), "item IDs must be unique")

    classified.sort(key=lambda item: (STATE_ORDER[item["queue_state"]], -item["review_score"], item["id"]))
    for rank, item in enumerate(classified, start=1):
        item["review_rank"] = rank

    return {
        "schema_version": SCHEMA_VERSION,
        "platform": platform,
        "captured_at": data["captured_at"],
        "subject": data["subject"],
        "score_interpretation": "human_review_order_only",
        "items": classified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a human review queue from verified public conversation items.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    try:
        output = build_review_queue(data)
    except QueueError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built review queue {args.input} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
