#!/usr/bin/env python3
"""Validate a bounded, visible social conversation review plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "visible-conversation-run-v1"
PLATFORMS = {"douyin", "xiaohongshu"}
ACCESS_ROUTES = {"visible_browser", "manual_links", "official_api", "written_permission"}
REQUIRED_STOPS = {
    "captcha",
    "account_challenge",
    "rate_limit",
    "login_expired",
    "permission_prompt",
    "platform_warning",
    "unexpected_redirect",
    "target_mismatch",
    "repeated_read_failure",
}
DISABLED_PERMISSIONS = {
    "like",
    "save",
    "follow",
    "comment",
    "publish",
    "edit",
    "delete",
    "message",
    "export_credentials",
    "identity_masking",
    "network_rotation",
    "challenge_solving",
}


class PlanError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


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


def validate_run_plan(data: dict[str, Any]) -> dict[str, Any]:
    require(data.get("schema_version") == SCHEMA_VERSION, f"schema_version must be {SCHEMA_VERSION}")

    platform = data.get("platform")
    require(platform in PLATFORMS, "platform must be douyin or xiaohongshu")
    require(isinstance(data.get("subject"), str) and data["subject"].strip(), "subject is required")

    access_route = data.get("access_route")
    require(access_route in ACCESS_ROUTES, "access_route is unsupported")

    operator = require_object(data.get("operator"), "operator")
    require(require_bool(operator.get("user_started"), "operator.user_started"), "operator.user_started must be true")
    require(
        require_bool(operator.get("account_owner_confirmed"), "operator.account_owner_confirmed"),
        "operator.account_owner_confirmed must be true",
    )
    require_bool(operator.get("login_completed_by_human"), "operator.login_completed_by_human")
    visible_browser = require_bool(operator.get("visible_browser"), "operator.visible_browser")
    if access_route == "visible_browser":
        require(visible_browser, "visible_browser route requires operator.visible_browser=true")
        require(operator["login_completed_by_human"], "visible_browser route requires human-completed login")

    limits = require_object(data.get("limits"), "limits")
    require_int(limits.get("queries"), "limits.queries", 1, 3)
    require_int(limits.get("list_items_seen"), "limits.list_items_seen", 1, 24)
    detail_pages = require_int(limits.get("detail_pages"), "limits.detail_pages", 3, 8)
    require_int(limits.get("public_comments_per_page"), "limits.public_comments_per_page", 0, 3)
    require_int(limits.get("account_profile_reads"), "limits.account_profile_reads", 0, 1)
    require_int(limits.get("account_posts_sampled"), "limits.account_posts_sampled", 0, 5)

    delivery = require_object(data.get("delivery"), "delivery")
    minimum_pages = require_int(delivery.get("minimum_pages"), "delivery.minimum_pages", 3, 5)
    goal_pages = require_int(delivery.get("goal_pages"), "delivery.goal_pages", 3, 5)
    maximum_pages = require_int(delivery.get("maximum_pages"), "delivery.maximum_pages", 3, 5)
    require(minimum_pages <= goal_pages <= maximum_pages, "delivery must satisfy minimum <= goal <= maximum")
    require(detail_pages >= maximum_pages, "limits.detail_pages must cover delivery.maximum_pages")
    require(delivery.get("responses_per_page") == 3, "delivery.responses_per_page must equal 3")

    cadence = require_object(data.get("cadence"), "cadence")
    require(require_bool(cadence.get("single_flight"), "cadence.single_flight"), "cadence.single_flight must be true")
    require_int(cadence.get("discovery_wait_seconds"), "cadence.discovery_wait_seconds", 15, 3600)
    require_int(cadence.get("page_wait_seconds"), "cadence.page_wait_seconds", 20, 3600)
    require_int(cadence.get("cooldown_after_reads"), "cadence.cooldown_after_reads", 1, 5)
    require_int(cadence.get("cooldown_seconds"), "cadence.cooldown_seconds", 45, 7200)
    require(not require_bool(cadence.get("jitter"), "cadence.jitter"), "cadence.jitter must be false")

    permissions = require_object(data.get("permissions"), "permissions")
    for key in sorted(DISABLED_PERMISSIONS):
        require(key in permissions, f"permissions.{key} is required")
        require(not require_bool(permissions[key], f"permissions.{key}"), f"permissions.{key} must be false")

    stops = data.get("stop_conditions")
    require(isinstance(stops, list) and all(isinstance(item, str) for item in stops), "stop_conditions must be strings")
    missing_stops = sorted(REQUIRED_STOPS - set(stops))
    require(not missing_stops, "missing stop conditions: " + ", ".join(missing_stops))

    reviewed_at = data.get("rule_reviewed_at")
    require(isinstance(reviewed_at, str) and len(reviewed_at) == 10, "rule_reviewed_at must be YYYY-MM-DD")
    require_int(data.get("raw_evidence_days"), "raw_evidence_days", 1, 30)

    return {
        "schema_version": SCHEMA_VERSION,
        "platform": platform,
        "access_route": access_route,
        "status": "accepted",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a visible social conversation run plan.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    raw = args.input.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    try:
        receipt = validate_run_plan(data)
    except PlanError as exc:
        parser.error(str(exc))

    receipt["input_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Accepted {args.input} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

