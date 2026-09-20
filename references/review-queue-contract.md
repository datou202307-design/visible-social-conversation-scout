# Human review queue contract

`scripts/rank_review_queue.py` accepts UTF-8 JSON using `social-review-queue-v1`.

## Input

```json
{
  "schema_version": "social-review-queue-v1",
  "platform": "xiaohongshu",
  "captured_at": "2026-09-20T10:00:00Z",
  "subject": "synthetic example topic",
  "run_plan_receipt": {
    "status": "accepted",
    "input_sha256": "64 lowercase hexadecimal characters"
  },
  "voice_context": {
    "source": "current_account_public_posts",
    "profile_reads": 1,
    "posts_sampled": 3,
    "confidence": "medium",
    "patterns": ["short sentences supported by repeated samples"],
    "source_ids": ["synthetic-post-1", "synthetic-post-2"]
  },
  "items": [
    {
      "id": "xiaohongshu:synthetic-note-1",
      "content_id": "synthetic-note-1",
      "source_url": "https://example.invalid/xiaohongshu/synthetic-note-1",
      "public_author_label": "synthetic creator",
      "title": "Synthetic public conversation",
      "evidence": {
        "target_matched": true,
        "understanding": "verified_page",
        "sensitive_topic": false,
        "public_excerpt": "Synthetic evidence only"
      },
      "public_counters": {
        "likes": 240,
        "comments": 18,
        "saves": 31
      },
      "observations": {
        "subject_overlap": 4,
        "contribution_specificity": 4,
        "audience_continuity": 2,
        "attention_evidence": 2,
        "response_space": 2,
        "evidence_strength": 5
      },
      "penalties": {
        "saturation": 1,
        "uncertainty": 0
      },
      "relationship_disclosure_required": false,
      "disclosure_reviewed": false,
      "limitations": []
    }
  ]
}
```

## Observation scales

| Observation | Range | Meaning |
|---|---:|---|
| `subject_overlap` | 0–4 | How directly verified page evidence matches the declared subject |
| `contribution_specificity` | 0–4 | Whether the account can respond with a concrete, supported point |
| `audience_continuity` | 0–3 | Continuity between this public conversation and the account's established audience |
| `attention_evidence` | 0–3 | Strength of capture-time public attention indicators under the run's declared threshold |
| `response_space` | 0–3 | Whether there is still room for a useful human response without assuming future reach |
| `evidence_strength` | 0–5 | Target identity and content-understanding quality |

Penalties are `saturation` from 0–3 and `uncertainty` from 0–5.

```text
review_score = sum(observations) - saturation - uncertainty
```

The score is clamped to zero. It orders human review only.

## Queue states

- `send_to_operator`: score at least 14, `subject_overlap >= 2`, `contribution_specificity >= 2`, `evidence_strength >= 4`, verified target, non-sensitive subject, and no unresolved relationship disclosure.
- `watchlist`: score 9–13 with adequate target evidence, or a stronger item with an unresolved non-blocking gap.
- `hold`: lower score, partial content understanding, or insufficient evidence for a page-specific response.
- `blocked`: sensitive topic, target mismatch, missing accepted run receipt, or a relationship disclosure requirement that has not been reviewed.

Only `send_to_operator` is ready for response drafting. Public counters are recorded as facts but do not directly calculate the score; the reviewer must interpret them against the run's declared platform and topic threshold.

## Voice context

The voice context may contain one public profile read and zero to five recent public posts from the current account. Use only repeated patterns. No private sources, sensitive-trait inference, distinctive phrase copying, or cross-account profiling are allowed.

