---
name: visible-social-conversation-scout
description: Run a small, human-controlled Douyin or Xiaohongshu review session in a visible browser, preserve three to five verified public conversation pages, and prepare three evidence-bound account-voice response options per page without performing platform writes.
---

# Visible Social Conversation Scout

Help an account operator find a small set of public conversations that deserve human attention. Keep the browser observable, establish what each page actually says, prioritize review with explicit evidence, prepare account-consistent response options, and stop before any platform write.

## Start from a run plan

Require one platform and either one understandable subject or an explicit request to derive one subject from the current account's public evidence. Infer ordinary search wording when possible. Ask one short question only when neither the platform nor a bounded subject-selection objective can be determined.

Before reading a platform, create `run-plan.json` from [references/run-plan-contract.md](references/run-plan-contract.md) and validate it:

```text
python scripts/check_run_plan.py --input run-plan.json --output run-plan-receipt.json
```

Then authorize the exact first visible platform read:

```text
python scripts/authorize_browser_read.py --plan run-plan.json --receipt run-plan-receipt.json --target-url https://www.xiaohongshu.com/ --output browser-read-authorization.json
```

Do not call a browser navigation, page read, adapter, or platform API until `browser-read-authorization.json` exists with `status: authorized`. The guard revalidates the plan, requires the receipt digest to match the exact plan bytes, binds the first read to the planned platform's HTTPS root, and rejects query parameters or fragments. If the plan changes, regenerate the receipt and authorization before another platform read.

The normal route is a user-started, visible browser session. The account owner completes login and account challenges personally. Manual links, a documented official API scope, or written platform permission are alternate routes. A logged-in browser is not platform approval.

Use one platform per run. A two-platform request becomes two separate plans, ledgers, review queues, and page sets.

When the operator asks for an account-matched subject, put that bounded selection objective in the plan before the first platform read. After the receipt is accepted, read only the current platform account's allowed public profile and post sample, then freeze one concrete subject in the ledger before the first search. Rebuild this subject for every platform; never carry a subject from another platform account. If there are no public posts, use only explicit public profile positioning to choose a broad subject, mark confidence `low`, and avoid adding traits from a username. Stop before search when public evidence cannot support even a broad subject.

## Preserve the operator boundary

Read [references/data-and-risk.md](references/data-and-risk.md) before live work.

- Keep search, page checks, waits, and page delivery visible to the operator whenever the interface permits it.
- Perform one browser read at a time. Use fixed minimum waits as load controls, never as an evasion claim.
- Do not vary fingerprints, network identity, headers, cursor paths, scrolling, or timing to imitate a person.
- Do not solve or bypass CAPTCHA, verification, rate limits, warnings, permission requests, or abnormal redirects.
- Never like, save, follow, comment, publish, delete, edit, or send a message.
- Never request or store passwords, cookies, tokens, browser profiles, HAR files, or session exports.
- Stop after a platform challenge or two consecutive failures of the same read. Do not switch accounts or adapters to continue past the stop.

## Build a small voice card

Read the current account's public profile once and sample no more than five recent public posts from that same account. Save only a minimized `voice-card.json`:

- explicit public positioning;
- recurring subjects supported by more than one sample;
- repeated length, punctuation, particle, emoji, formality, directness, and question habits;
- supported first-person facts;
- public source IDs, capture time, confidence, and limitations.

Do not inspect private messages, drafts, saved or liked content, creator analytics, contacts, browsing history, or non-public account data. Do not infer sensitive traits. If public examples are absent, set confidence to `low` and use short, ordinary, curious, low-claim wording.

## Gather and verify conversation items

Use the budgets accepted in `run-plan-receipt.json`. Observe only enough search results to fill the review queue. Open details sequentially. For each retained item, record:

- stable public content ID and canonical URL;
- minimized public author label and publication label;
- visible title, caption, body, subtitle, transcript, OCR, or human-reviewed evidence;
- visible counters with capture time;
- search phrase and observed position;
- evidence limitations.

A list card is not a verified page. Video-specific wording requires caption, subtitle, transcript, OCR, or human review. One snapshot does not prove growth, causality, audience composition, or platform-wide rank.

Remove expiring query parameters and signed values before saving or sharing. Do not package raw browser state or full-page archives.

## Build the human review queue

Read [references/review-queue-contract.md](references/review-queue-contract.md). Normalize verified items and run:

```text
python scripts/rank_review_queue.py --input review-items.json --output review-queue.json
```

The queue uses six bounded observations—subject overlap, contribution specificity, audience continuity, public attention evidence, remaining response space, and evidence strength—then subtracts saturation and uncertainty penalties. The resulting review score organizes human attention; it does not predict reach, engagement, or conversion.

Only items in `send_to_operator` state may receive response drafts. Sensitive topics, uncertain target identity, weak page understanding, missing authorization, or commercial disclosure gaps remain held or blocked.

## Prepare three response stances

For every delivered page, prepare exactly three clean options. Select from these stances:

- `page_detail`: react to one verified detail on the page;
- `bounded_practice`: add one small practice or context that the account can support without claiming results it does not have;
- `open_question`: ask one narrow question tied to an actual evidence gap;
- `declared_resource`: offer a relevant resource only when the author explicitly asks for one and the account relationship can be disclosed.

The default set is one `page_detail`, one `bounded_practice`, and one `open_question`. Replace `bounded_practice` with `declared_resource` only after disclosure review. When a supported practice is unavailable, write a second page-specific option with a different rhythm instead of inventing expertise.

Match the voice card using repeated evidence only. Do not copy a distinctive sentence, manufacture slang or emoji, or claim an experience, result, customer story, price, or endorsement without support.

Run a `voice_fit_review` before delivery. Reject generic praise, consultant framing, balanced mini-essays, repeated openings, forced closing questions, unsupported certainty, and wording noticeably longer or more polished than the account samples. Keep stance names, evidence, confidence, and uncertainty in metadata; the paste-ready line contains only the response.

When AI supplied the core wording, remind the operator to use the platform's current AI-content declaration when required. Resource or product references require clear account relationship and applicable commercial-content review.

## Deliver visible source pages

Read [references/visible-page-delivery.md](references/visible-page-delivery.md).

Deliver three to five distinct original pages in the same user-visible browser used for the run. As soon as an item qualifies:

1. allocate a dedicated visible tab;
2. open its canonical page and verify platform, content ID, and visible title or caption;
3. mark the tab for persistence using the host environment's supported mechanism;
4. record the page in `delivered-pages.json`;
5. tell the operator the page is ready, then continue the sequential search.

Keep one dedicated visible search workspace alongside the delivered pages. After the search settles, verify that its visible search field or query label contains the exact frozen query, retain that tab with the host persistence mechanism, and record the query-visible check. The search workspace is a trace of discovery and does not count toward the three-to-five original-page minimum.

Do not navigate or close a delivered tab. A search result, background page, headless context, CLI inventory, Markdown link, score, or offline card does not count as delivery. Before reporting success, re-list the same user-owned browser and verify both that the search workspace still displays the exact query and that every delivered tab still has its recorded title and URL.

## Finish with an operator packet

Return, for each delivered page:

- why it entered the review queue;
- verified evidence and limitations;
- captured public attention indicators;
- review score and queue state;
- three clean response options;
- voice-card confidence and `voice_fit_review` result;
- AI and commercial disclosure reminders;
- the visible page state `awaiting_operator`.

Save run artifacts in a new local directory. Never overwrite an earlier run. Publishing and final wording remain human actions.
