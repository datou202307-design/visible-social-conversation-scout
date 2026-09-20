# Visible page delivery

The primary deliverable is a set of three to five verified source pages that remain open in the account owner's visible browser.

Keep one separate visible search workspace open as discovery trace. Its search field or visible query label must show the exact frozen query at final verification. It is retained for operator inspection but never counts as one of the three to five source pages.

## Browser-neutral contract

The host environment must provide these capabilities:

1. select the user-owned browser instance carrying the logged-in account;
2. create a distinct visible tab without replacing an earlier delivered tab;
3. navigate to a canonical public URL;
4. read the tab's final URL and visible title or caption;
5. persist the tab beyond the agent turn;
6. enumerate user-visible tabs for final verification.

If any capability is missing, mark live delivery unsupported. Offline cards and links may still be returned, but they do not satisfy the visible-page acceptance condition.

## Delivery record

Store one item per page in `delivered-pages.json`:

```json
{
  "sequence": 1,
  "platform": "xiaohongshu",
  "content_id": "synthetic-note-1",
  "canonical_url": "https://example.invalid/xiaohongshu/synthetic-note-1",
  "browser_instance_label": "user-visible-browser",
  "tab_id": "host-generated-unique-id",
  "verified_at": "2026-09-20T10:00:00Z",
  "target_verified": true,
  "persistence_marked": true,
  "final_inventory_verified": true,
  "state": "awaiting_operator"
}
```

Never put cookies, session tokens, signed URL parameters, browser profile files, or credential material in this record.

Also store a top-level search-workspace record with the plain query, tab ID, `query_visible: true`, persistence status, and final-inventory status. Do not store signed result URLs. A tab that has fallen back to the home feed, displays an empty search box, or no longer shows the exact query fails this check and must be corrected before success is reported.

## Codex adapter note

In Codex computer-use environments, retain every finished delivery tab with `markDeliverable()` and verify the set through the connected browser's user-tab inventory. Use `markHandoff()` only for an unfinished page waiting for login, approval, CAPTCHA, or another human action.

Other hosts must map the same browser-neutral contract to their own documented persistence mechanism. Do not claim live delivery from a CLI-owned, headless, background, shared, or temporary tab.

## Final check

Before reporting success, verify that the search workspace still shows the exact query and that every recorded source tab remains distinct and shows the expected platform, content ID, title or caption, and canonical target. If the search workspace has lost the query or the visible inventory contains fewer source pages than the record, invalidate the delivery and correct only the missing tabs within the existing run budget.
