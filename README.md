# Visible Social Conversation Scout

English | [简体中文](README.zh-CN.md)

A Codex Skill for small, observable, human-controlled review sessions on Douyin and Xiaohongshu.

It helps an account operator collect a limited set of public conversation pages, verify what each page says, order them for human review, and draft account-consistent response options. It never publishes or performs other platform writes.

## Status

Version `0.5.0-rc.4` is a requirements-first public release candidate. It is not affiliated with or endorsed by Douyin, Xiaohongshu, OpenCLI, or DokoBot.

## Core behavior

- One platform and one visible browser session per run.
- One retained, query-visible search workspace as discovery trace; it does not count toward page delivery.
- Human-owned login and immediate human takeover.
- Fixed read budgets, sequential execution, and explicit stop conditions.
- Three to five verified original pages retained in the user's browser.
- Exactly three evidence-bound response options per page.
- Account voice derived from no more than five recent public posts.
- Optional account-matched topic selection, rebuilt from the current platform account's public evidence before search.
- No likes, saves, follows, comments, publishing, messages, credential export, challenge bypass, identity masking, or anti-detection behavior.

## Install as a Codex Skill

Copy this repository directory to:

```text
~/.codex/skills/visible-social-conversation-scout
```

The Skill becomes available on the next Codex turn. Invoke it explicitly with:

```text
Use $visible-social-conversation-scout to review one topic on Xiaohongshu in my visible logged-in browser. Deliver three original pages and three response options per page. Keep all platform writes disabled.
```

Or ask it to choose one topic that matches the current platform account:

```text
Use $visible-social-conversation-scout on Douyin and derive one topic from the current account's public profile and up to five public posts. Freeze that topic before search, then deliver three original pages with three response options each. Keep all platform writes disabled.
```

## Dependencies

- Python 3.10 or newer for the bundled validators.
- A host environment capable of controlling and retaining visible browser tabs.
- Optional external adapters such as OpenCLI or DokoBot. They are not bundled.

Adapter availability does not grant permission to automate a platform. Review current platform rules and applicable law before every run.

## Validate locally

```text
python -m unittest discover -s tests -v
python scripts/check_run_plan.py --input examples/run-plan.example.json --output run-plan-receipt.json
python scripts/authorize_browser_read.py --plan examples/run-plan.example.json --receipt run-plan-receipt.json --target-url https://www.xiaohongshu.com/ --output browser-read-authorization.json
python scripts/rank_review_queue.py --input examples/review-items.example.json --output review-queue.json
```

## Repository map

- `SKILL.md` — agent-facing workflow and boundaries.
- `references/` — run plan, review queue, data handling, and visible page delivery contracts.
- `scripts/` — deterministic standard-library validators.
- `examples/` — synthetic inputs with no real account or platform session data.
- `tests/` — behavior-focused unit tests.

## License and attribution

Licensed under Apache-2.0. See `LICENSE`, `NOTICE`, and `THIRD_PARTY.md`.
