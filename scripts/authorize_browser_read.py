#!/usr/bin/env python3
"""Authorize the first visible platform read for an accepted run plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from check_run_plan import PlanError, validate_run_plan


GATE_SCHEMA_VERSION = "browser-read-authorization-v1"
ALLOWED_HOSTS = {
    "douyin": {"douyin.com", "www.douyin.com"},
    "xiaohongshu": {"xiaohongshu.com", "www.xiaohongshu.com"},
}


class GateError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def authorize_browser_read(plan_raw: bytes, receipt: dict[str, Any], target_url: str) -> dict[str, Any]:
    try:
        plan = json.loads(plan_raw.decode("utf-8"))
        validated = validate_run_plan(plan)
    except (UnicodeDecodeError, json.JSONDecodeError, PlanError) as exc:
        raise GateError(f"run plan is not valid: {exc}") from exc

    plan_sha256 = hashlib.sha256(plan_raw).hexdigest()
    require(receipt.get("status") == "accepted", "run-plan receipt status must be accepted")
    require(receipt.get("schema_version") == validated["schema_version"], "receipt schema does not match plan")
    require(receipt.get("platform") == validated["platform"], "receipt platform does not match plan")
    require(receipt.get("access_route") == validated["access_route"], "receipt access route does not match plan")
    require(receipt.get("input_sha256") == plan_sha256, "receipt digest does not match the exact run plan")

    parsed = urlparse(target_url)
    require(parsed.scheme == "https", "first browser read must use HTTPS")
    require(not parsed.username and not parsed.password, "first browser read URL must not contain credentials")
    host = (parsed.hostname or "").lower()
    require(host in ALLOWED_HOSTS[validated["platform"]], "first browser read host does not match the plan platform")
    require(not parsed.query and not parsed.fragment, "first browser read URL must not contain query parameters or fragments")

    return {
        "schema_version": GATE_SCHEMA_VERSION,
        "status": "authorized",
        "platform": validated["platform"],
        "access_route": validated["access_route"],
        "subject": plan["subject"],
        "plan_sha256": plan_sha256,
        "first_read_url": target_url,
        "first_read_host": host,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Authorize the first visible browser read for an accepted run plan.")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    plan_raw = args.plan.read_bytes()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    try:
        authorization = authorize_browser_read(plan_raw, receipt, args.target_url)
    except GateError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(authorization, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Authorized first browser read -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
