---
name: visible-social-conversation-scout
description: Review one Douyin or Xiaohongshu topic in a user-visible browser, retain three to five verified public pages, and prepare three account-voice response options per page for human review without platform writes.
---

# Douyin & Xiaohongshu AI Conversation Scout

Find a small set of public conversations for an account operator to review. Keep the browser observable, ground every decision in visible evidence, and stop before any platform write.

## Non-negotiable contract

- One platform and one frozen subject per run; split a two-platform request into separate runs.
- Use the account owner's visible browser, one read at a time, with the validated waits and budgets.
- The owner completes login and account challenges. Never request or store credentials, cookies, tokens, profiles, HAR files, or session exports.
- Stop on CAPTCHA, account challenge, rate limit, expired login, permission prompt, platform warning, abnormal redirect, target mismatch, unexpected private data, or two failures of the same read. Do not switch accounts, adapters, devices, or networks to continue past a stop.
- Do not vary identity, fingerprint, headers, network, cursor, scrolling, or timing to imitate a person or avoid controls.
- Never like, save, follow, comment, publish, edit, delete, or message. The operator owns final wording and publishing.
- Deliver three to five verified original pages plus one retained search workspace showing the exact frozen query. Prepare exactly three review-only responses per page.
- Do not claim reach, growth, causality, platform approval, or content understanding beyond the recorded evidence.

## 1. Authorize the run

Review current platform rules and record the date. After the owner confirms the bounded run and completes login, prepare the default visible-browser artifacts in a new directory:

```text
python scripts/start_run.py --platform xiaohongshu --subject "bounded subject or account-matching objective" --rule-reviewed-at YYYY-MM-DD --operator-confirmed --human-login-complete --output-dir runs/<new-run-id>
```

The command creates `run-plan.json`, `run-plan-receipt.json`, and `browser-read-authorization.json` without overwriting an earlier run. Do not navigate, read a page, call an adapter, or use a platform API unless authorization status is `authorized`.

Read [references/run-plan-contract.md](references/run-plan-contract.md) only when using a non-browser route or changing default budgets. Any plan change requires a new receipt and authorization.

For an account-matched subject, put the bounded selection objective in the plan. After authorization, read only the current platform account's public profile once and up to five recent public posts, then freeze one concrete subject before search. Rebuild it for each platform. With no public posts, use explicit profile positioning for a broad, `low`-confidence subject or stop.

## 2. Observe within the boundary

Before live platform work, read [references/data-and-risk.md](references/data-and-risk.md).

Create a minimized `voice-card.json` from repeated public evidence: positioning, recurring subjects, sentence length, punctuation, particles, emoji, formality, directness, question habits, supported first-person facts, source IDs, capture time, confidence, and limitations. Do not inspect private or behavioral account data or infer sensitive traits.

Search only within the accepted budget. Open details sequentially and keep compact evidence: stable content ID, canonical URL, minimized public author and publication labels, necessary title/body/caption/subtitle/transcript/OCR evidence, visible counters with capture time, query, observed position, and limitations. A list card is not a verified page; video-specific wording requires subtitle, transcript, OCR, or human review. Remove signed or expiring parameters and do not save full-page dumps or browser state.

Keep detailed evidence and the operation ledger on disk. Return concise stage summaries and exceptions to the conversation instead of full DOM, page text, or ledger output.

## 3. Rank verified candidates

When verified candidates exist, read [references/review-queue-contract.md](references/review-queue-contract.md), create `review-items.json`, and run:

```text
python scripts/rank_review_queue.py --input review-items.json --output review-queue.json
```

The score orders human attention; it does not predict performance. Draft only for `send_to_operator`. Hold or block sensitive topics, uncertain targets, partial understanding, missing authorization, and unresolved relationship disclosure.

## 4. Prepare three responses

For each deliverable page, prepare exactly three evidence-bound options:

- `page_detail`: respond to one verified page detail;
- `bounded_practice`: add one small, supportable practice or context;
- `open_question`: ask one narrow question tied to an evidence gap;
- `declared_resource`: replace `bounded_practice` only when the author requested a resource and disclosure was reviewed.

Use repeated voice-card evidence only. Reject generic praise, consultant framing, balanced mini-essays, repeated openings, forced closing questions, unsupported certainty, distinctive phrase copying, invented experience, and wording substantially more polished or longer than the account samples. Keep stance, evidence, confidence, uncertainty, and `voice_fit_review` in metadata; the paste-ready line contains only the response.

Remind the operator to apply current AI-content labeling when required. Product, service, offer, link, recommendation, or resource references require truthful relationship disclosure and commercial-content review.

## 5. Deliver visible pages

When the first item reaches `send_to_operator`, read [references/visible-page-delivery.md](references/visible-page-delivery.md).

Open every qualified canonical page in a distinct visible tab, verify its platform, ID, title or caption, mark it persistent with the host mechanism, and record it in `delivered-pages.json`. Tell the operator the page is retained, then continue the sequential search. Never navigate or close a delivered tab.

Retain one separate visible search workspace whose field or label shows the exact frozen query; it is discovery evidence and does not count toward the three-to-five page minimum. Before success, enumerate the same user-owned browser and verify the query, titles, URLs, distinct tabs, and persistence marks. Headless pages, CLI inventories, links, cards, scores, or background tabs do not count as delivery.

## 6. Hand off to the operator

For every delivered page return: selection reason, verified evidence and limitations, captured public indicators, review score and queue state, three clean responses, voice confidence and review result, disclosure reminders, and visible state `awaiting_operator`.

Save all artifacts in the new run directory. Never overwrite an earlier run. Report three or four retained source pages as minimum met but goal unmet, fewer than three as incomplete, and five as goal achieved. Publishing remains a human action.
