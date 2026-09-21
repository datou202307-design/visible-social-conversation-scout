# Run plan contract

Every browser-assisted run starts with a `visible-conversation-run-v1` plan. The plan is an operator-visible boundary, not a claim that the platform permits the operation.

For the default visible-browser route, prefer `scripts/start_run.py`; it creates the plan, accepted receipt, and first-read authorization together in a new directory. Use the full contract below when changing budgets or using `manual_links`, `official_api`, or `written_permission`.

`subject` normally contains the concrete review topic. When the operator explicitly asks the Skill to match the current account, it may instead contain a bounded selection objective such as “derive one subject from the current account's public profile and up to five public posts.” The receipt must still be accepted before the first platform read. After that limited account read, freeze one concrete subject in the ledger before search. Do this separately for every platform; do not reuse another platform account's subject. If public evidence is insufficient, either select a broad profile-supported subject with `low` confidence or stop before search.

## Required shape

```json
{
  "schema_version": "visible-conversation-run-v1",
  "platform": "xiaohongshu",
  "subject": "synthetic example topic",
  "access_route": "visible_browser",
  "operator": {
    "user_started": true,
    "account_owner_confirmed": true,
    "login_completed_by_human": true,
    "visible_browser": true
  },
  "limits": {
    "queries": 3,
    "list_items_seen": 24,
    "detail_pages": 8,
    "public_comments_per_page": 3,
    "account_profile_reads": 1,
    "account_posts_sampled": 5
  },
  "delivery": {
    "minimum_pages": 3,
    "goal_pages": 5,
    "maximum_pages": 5,
    "responses_per_page": 3
  },
  "cadence": {
    "single_flight": true,
    "discovery_wait_seconds": 15,
    "page_wait_seconds": 20,
    "cooldown_after_reads": 5,
    "cooldown_seconds": 45,
    "jitter": false
  },
  "permissions": {
    "like": false,
    "save": false,
    "follow": false,
    "comment": false,
    "publish": false,
    "edit": false,
    "delete": false,
    "message": false,
    "export_credentials": false,
    "identity_masking": false,
    "network_rotation": false,
    "challenge_solving": false
  },
  "stop_conditions": [
    "captcha",
    "account_challenge",
    "rate_limit",
    "login_expired",
    "permission_prompt",
    "platform_warning",
    "unexpected_redirect",
    "target_mismatch",
    "repeated_read_failure"
  ],
  "rule_reviewed_at": "2026-09-20",
  "raw_evidence_days": 14
}
```

## Accepted routes

- `visible_browser`: the account owner starts a bounded run in a visible logged-in browser.
- `manual_links`: a human supplies a small set of public links and needed excerpts.
- `official_api`: the operation is inside a documented official API scope.
- `written_permission`: platform permission covers the account, data, purpose, and time period.

The validator accepts only Douyin and Xiaohongshu in v1. It requires single-flight execution, fixed minimum waits, three to five delivered pages, exactly three response options per page, no platform write permission, and the complete stop set.

Users may lower read budgets, lengthen waits, or shorten raw-evidence retention. They cannot enable writes, challenge handling, identity masking, network rotation, jitter, hidden browsing, or parallel reads within this contract.

## Receipt

`scripts/check_run_plan.py` writes a receipt containing the schema, platform, validation status, and SHA-256 of the exact input bytes. Store the receipt beside the run ledger. Any plan change requires a new receipt before another platform read.

## First-read authorization

After the receipt is accepted and before any browser navigation or adapter call, run `scripts/authorize_browser_read.py`. The guard revalidates the plan, verifies the receipt digest against the exact plan bytes, and binds the first read to the planned platform's HTTPS root without query parameters or fragments. A run may access the platform only when the resulting `browser-read-authorization.json` has `status: authorized`. Plan changes invalidate the authorization and require a new receipt and authorization.
