---
name: gmail-cli
description: Use Gmail through the authenticated Google Workspace CLI. Use when the bundled Gmail connector cannot expose raw message payloads, binary attachments, unsupported MIME types, original MIME source, or exact Gmail API metadata.
---

# Gmail (CLI)

Use this plugin when Gmail access needs the raw Google Workspace CLI path, especially for binary attachments, unsupported MIME types, raw message payloads, label IDs, original MIME source, or exact API metadata that the bundled Gmail connector cannot return.

This plugin is a derivative of OpenAI's Gmail connector plugin and packages the
same canonical Gmail app registration. Prefer the bundled connector for normal
mailbox search, thread summaries, drafts, sends, archive/delete actions, and
user-friendly inbox triage. Use the installed `gws` CLI as the precise fallback.

## Start

```bash
command -v gws
gws auth status
gws gmail users getProfile --params '{"userId":"me"}'
```

If Gmail commands fail with `API not enabled`, the OAuth account can be valid while the Google Cloud project still lacks `gmail.googleapis.com`. Enable Gmail API for the project shown by `gws auth status`, wait briefly, then retry.

## Search And Inspect

Prefer Gmail search syntax for message discovery:

```bash
gws gmail users messages list --params '{"userId":"me","q":"from:bbva has:attachment newer_than:1y","maxResults":10}'
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"metadata","metadataHeaders":["From","To","Subject","Date"]}'
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"full"}'
```

For a broad source-processing request, use the caller's explicit received-time
span or default an omission to the previous 24 hours ending at invocation time.
Express the window in the Gmail query with `after:` and `before:` and verify
exact inclusion against `internalDate` when boundary precision matters. Never
default a broad request to all mailbox history. Exact message IDs and explicitly
bounded thread context need no additional time span, and a repeated window may
intentionally revisit the same messages.

Use `format=metadata` for first-pass reads and `format=full` only for shortlisted messages where payload parts, attachment IDs, or headers matter.

Use bounded pagination when needed:

```bash
gws gmail users messages list --params '{"userId":"me","q":"has:attachment filename:pdf newer_than:2y","maxResults":100}' --page-all --page-limit 3
```

## Scheduled attention window

`gmail-attention` owns the stateless received-time scan used by
`google-cloud:gmail-review-attention`:

```bash
gmail-attention scan
gmail-attention scan --since 48h
gmail-attention scan --since 2026-08-10T12:00:00Z --until 2026-08-12T12:00:00Z
```

An omitted start means the previous 24 hours. The same explicit window returns
the same source messages; there is no semantic processed cursor or commit step.
Sent, draft, chat, spam, and trash messages are excluded.

## Attachments

List attachments in a shortlisted message:

```bash
python3 scripts/gmail_cli.py attachments --message-id MESSAGE_ID
```

Download by filename:

```bash
python3 scripts/gmail_cli.py download-attachment \
  --message-id MESSAGE_ID \
  --filename "Contrato Digital.zip" \
  --output ./Contrato-Digital.zip
```

Download by Gmail attachment ID:

```bash
python3 scripts/gmail_cli.py download-attachment \
  --message-id MESSAGE_ID \
  --attachment-id ATTACHMENT_ID \
  --output ./attachment.bin
```

Resolve `scripts/gmail_cli.py` relative to the google-cloud plugin root. If you are reading this skill from a plugin cache path, the helper is two directories above this skill file at `../../scripts/gmail_cli.py`.

The helper decodes Gmail's base64url `data` field and writes the binary bytes. Verify the downloaded artifact before relying on it:

```bash
ls -lh ./Contrato-Digital.zip
file ./Contrato-Digital.zip
unzip -l ./Contrato-Digital.zip
```

For password-protected ZIPs or PDFs, use the password instructions from the email body. Do not guess or expose sensitive identifiers in public docs.

## Raw MIME

Use raw format when exact original MIME content matters:

```bash
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"raw"}'
```

Decode the returned `raw` field as base64url if you need to inspect the original `.eml` locally.

## Labels And Mutations

Prefer the bundled Gmail connector for user-facing archive/delete/label/draft/send actions. If a raw CLI mutation is necessary, read the target message first and use a dry-run-style preview in your explanation before applying changes.

Common read commands:

```bash
gws gmail users labels list --params '{"userId":"me"}'
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"metadata"}'
```

## Raw API Help

Use schema discovery before unfamiliar fields or methods:

```bash
gws schema gmail.users.messages.list --resolve-refs
gws schema gmail.users.messages.get --resolve-refs
gws schema gmail.users.messages.attachments.get --resolve-refs
gws schema gmail.users.labels.list --resolve-refs
```

## Rules

- Prefer message IDs over subjects; subjects and sender names are not unique.
- Prefer metadata-only discovery before reading bodies or full payloads.
- Use the bundled Gmail connector first for normal search/read/thread/draft workflows; use `gws` when raw payload or binary attachment handling matters.
- Read before archive, delete, label, send, or draft mutations. Ask before destructive mailbox changes unless the user already explicitly approved the exact action.
- Keep downloaded email artifacts in the current workspace or a clearly named temporary folder, and verify file type/size after download.
- Treat raw attachments, contracts, bank docs, IDs, and policy documents as private. Do not paste sensitive numbers into generated public docs or messages unless the user explicitly asks.
