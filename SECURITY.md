# Security policy

## Supported version

Security fixes are applied to the latest tagged release candidate until the project declares a stable release.

## Reporting

Use GitHub private vulnerability reporting when it is enabled for the repository. Do not open a public issue containing credentials, signed URLs, account identifiers, browser state, personal data, or platform incident evidence.

Include only the minimum information needed to reproduce the problem with synthetic data. Maintainers may request a redacted local receipt or validator output; they will not request passwords, cookies, tokens, browser profiles, HAR files, private messages, drafts, or creator analytics.

## Secrets and session data

Never commit:

- `.env` files or credentials;
- cookies, tokens, API keys, signed navigation parameters, or session exports;
- Chrome profiles, extension storage, browser databases, HAR files, or captured request headers;
- real run directories, screenshots, full-page archives, account voice samples, or delivered-page inventories;
- private messages, drafts, saved content, liked content, contacts, or unpublished analytics.

Examples and tests must use `example.invalid`, synthetic identifiers, and invented counters.

## Out-of-scope features

Reports requesting or implementing automatic social publishing, challenge bypass, account rotation, identity masking, fingerprint manipulation, network rotation, private-data collection, or anti-detection behavior will be closed as out of scope.

