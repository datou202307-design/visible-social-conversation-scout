# Contributing

Contributions should improve evidence quality, portability, operator control, documentation, or deterministic local validation.

## Development rules

- Use synthetic examples. Never commit live account or platform session data.
- Preserve the visible, user-started, single-flight, draft-only boundary.
- Do not add automatic likes, saves, follows, comments, publishing, edits, deletion, or messages.
- Do not add challenge handling, stealth, identity masking, network rotation, randomized imitation, or platform-control bypass.
- Do not copy text, templates, schemas, or code from an unlicensed source.
- Keep platform-specific mechanics in references or adapters; keep `SKILL.md` focused on the shared contract.
- Use only the Python standard library unless a dependency has a clear, reviewed benefit.

## Tests

Run before opening a pull request:

```text
python -m unittest discover -s tests -v
python scripts/check_run_plan.py --input examples/run-plan.example.json --output run-plan-receipt.json
python scripts/rank_review_queue.py --input examples/review-items.example.json --output review-queue.json
```

Tests should verify observable decisions and rejection boundaries. Avoid tests that merely match prose or generated wording.

## Pull requests

Explain the user problem, the resulting behavior, the validation performed, and any change to platform, privacy, disclosure, or browser-control risk. Changes to run budgets, stop conditions, queue thresholds, data fields, or write boundaries require explicit maintainer review.

