#!/usr/bin/env python3
"""Create and authorize a bounded visible-browser review run without overwriting prior artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from authorize_browser_read import authorize_browser_read
from check_run_plan import DISABLED_PERMISSIONS, REQUIRED_STOPS, validate_run_plan


PLATFORM_ROOTS = {
    "douyin": "https://www.douyin.com/",
    "xiaohongshu": "https://www.xiaohongshu.com/",
}
ARTIFACT_NAMES = (
    "run-plan.json",
    "run-plan-receipt.json",
    "browser-read-authorization.json",
)


class StartRunError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StartRunError(message)


def validate_review_date(value: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise StartRunError("rule_reviewed_at must be YYYY-MM-DD") from exc
    require(parsed <= date.today(), "rule_reviewed_at cannot be in the future")
    return value


def build_plan(
    *,
    platform: str,
    subject: str,
    rule_reviewed_at: str,
    operator_confirmed: bool,
    human_login_complete: bool,
    queries: int = 3,
    list_items_seen: int = 24,
    detail_pages: int = 8,
    public_comments_per_page: int = 3,
    account_posts_sampled: int = 5,
    minimum_pages: int = 3,
    goal_pages: int = 5,
    maximum_pages: int = 5,
    discovery_wait_seconds: int = 15,
    page_wait_seconds: int = 20,
    cooldown_after_reads: int = 5,
    cooldown_seconds: int = 45,
    raw_evidence_days: int = 14,
) -> dict[str, Any]:
    require(platform in PLATFORM_ROOTS, "platform must be douyin or xiaohongshu")
    require(bool(subject.strip()), "subject is required")
    require(operator_confirmed, "the account owner must confirm the bounded run")
    require(human_login_complete, "the account owner must complete login personally")

    return {
        "schema_version": "visible-conversation-run-v1",
        "platform": platform,
        "subject": subject.strip(),
        "access_route": "visible_browser",
        "operator": {
            "user_started": True,
            "account_owner_confirmed": True,
            "login_completed_by_human": True,
            "visible_browser": True,
        },
        "limits": {
            "queries": queries,
            "list_items_seen": list_items_seen,
            "detail_pages": detail_pages,
            "public_comments_per_page": public_comments_per_page,
            "account_profile_reads": 1,
            "account_posts_sampled": account_posts_sampled,
        },
        "delivery": {
            "minimum_pages": minimum_pages,
            "goal_pages": goal_pages,
            "maximum_pages": maximum_pages,
            "responses_per_page": 3,
        },
        "cadence": {
            "single_flight": True,
            "discovery_wait_seconds": discovery_wait_seconds,
            "page_wait_seconds": page_wait_seconds,
            "cooldown_after_reads": cooldown_after_reads,
            "cooldown_seconds": cooldown_seconds,
            "jitter": False,
        },
        "permissions": {key: False for key in sorted(DISABLED_PERMISSIONS)},
        "stop_conditions": sorted(REQUIRED_STOPS),
        "rule_reviewed_at": validate_review_date(rule_reviewed_at),
        "raw_evidence_days": raw_evidence_days,
    }


def prepare_run(output_dir: Path, **plan_options: Any) -> dict[str, Any]:
    if output_dir.exists():
        require(output_dir.is_dir(), "output_dir exists and is not a directory")
        require(not any(output_dir.iterdir()), "output_dir must be new or empty; prior runs are never overwritten")

    plan = build_plan(**plan_options)
    receipt_base = validate_run_plan(plan)
    plan_raw = (json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    receipt = {
        **receipt_base,
        "input_sha256": hashlib.sha256(plan_raw).hexdigest(),
    }
    authorization = authorize_browser_read(plan_raw, receipt, PLATFORM_ROOTS[plan["platform"]])

    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "run-plan.json": plan,
        "run-plan-receipt.json": receipt,
        "browser-read-authorization.json": authorization,
    }
    for name, payload in payloads.items():
        (output_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return authorization


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and authorize a visible social review run.")
    parser.add_argument("--platform", required=True, choices=sorted(PLATFORM_ROOTS))
    parser.add_argument("--subject", required=True)
    parser.add_argument("--rule-reviewed-at", required=True)
    parser.add_argument("--operator-confirmed", action="store_true")
    parser.add_argument("--human-login-complete", action="store_true")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--queries", type=int, default=3)
    parser.add_argument("--list-items-seen", type=int, default=24)
    parser.add_argument("--detail-pages", type=int, default=8)
    parser.add_argument("--public-comments-per-page", type=int, default=3)
    parser.add_argument("--account-posts-sampled", type=int, default=5)
    parser.add_argument("--minimum-pages", type=int, default=3)
    parser.add_argument("--goal-pages", type=int, default=5)
    parser.add_argument("--maximum-pages", type=int, default=5)
    parser.add_argument("--discovery-wait-seconds", type=int, default=15)
    parser.add_argument("--page-wait-seconds", type=int, default=20)
    parser.add_argument("--cooldown-after-reads", type=int, default=5)
    parser.add_argument("--cooldown-seconds", type=int, default=45)
    parser.add_argument("--raw-evidence-days", type=int, default=14)
    args = parser.parse_args()

    try:
        authorization = prepare_run(
            output_dir=args.output_dir,
            platform=args.platform,
            subject=args.subject,
            rule_reviewed_at=args.rule_reviewed_at,
            operator_confirmed=args.operator_confirmed,
            human_login_complete=args.human_login_complete,
            queries=args.queries,
            list_items_seen=args.list_items_seen,
            detail_pages=args.detail_pages,
            public_comments_per_page=args.public_comments_per_page,
            account_posts_sampled=args.account_posts_sampled,
            minimum_pages=args.minimum_pages,
            goal_pages=args.goal_pages,
            maximum_pages=args.maximum_pages,
            discovery_wait_seconds=args.discovery_wait_seconds,
            page_wait_seconds=args.page_wait_seconds,
            cooldown_after_reads=args.cooldown_after_reads,
            cooldown_seconds=args.cooldown_seconds,
            raw_evidence_days=args.raw_evidence_days,
        )
    except (StartRunError, ValueError) as exc:
        parser.error(str(exc))

    print(
        "Prepared authorized run: "
        f"platform={authorization['platform']} "
        f"subject={authorization['subject']!r} "
        f"output_dir={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
