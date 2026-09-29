# Label Actions

Use `gws gmail users labels list` to resolve names to IDs. Search with `messages
list` and a precise `q`, inspect the intended set, then pass explicit IDs to
`messages modify` or `messages batchModify`. See the
[mutation reference](../../gmail-cli/references/compose-and-mutations.md).

- Gmail API uses `addLabelIds` and `removeLabelIds` arrays, not label names.
- Create a missing label with `users labels create` only when authorized.
- For query-wide changes, enumerate all pages before applying changes so that
  the mutations do not change the search under pagination. State the scope and
  coverage; do not report a partial enumeration as all matching mail.
- Batch modifications accept at most 1,000 message IDs per request.
- Archive removes `INBOX`; trash uses `messages trash`. Permanent deletion is a
  separate destructive operation, never a substitute for archive or trash.
- Verify changed labels afterward. Separate applied changes from suggestions.
