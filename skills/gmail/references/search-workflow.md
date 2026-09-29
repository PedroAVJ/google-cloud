# Search Workflow

Use `gws gmail users messages list` with Gmail syntax in `q`. List results contain
only IDs and thread IDs: get each shortlisted message with `format=metadata`
for headers, snippets, labels, and `internalDate`. Start around 20 results.
Commands and authentication are in [gmail-cli](../../gmail-cli/SKILL.md).

1. Scope the query to the user's sender, topic, inbox, unread state, or dates.
   Broad source review defaults to the previous 24 hours; a precise requested
   older topic or date range takes precedence.
2. Use `labelIds` arrays for known IDs or `label:NAME` in `q` for name search.
   Include `includeSpamTrash=true` only when needed; `in:anywhere` alone should
   not be assumed to override the API flag.
3. Preserve the same query and pass `nextPageToken` as `pageToken`. Bound the
   page count, report partial coverage, and do not treat `resultSizeEstimate`
   as an exact count. Use message `internalDate` for dates and ordering rather
   than assuming the first page proves what is newest across an entire scope.
4. Refine noisy searches before reading bodies. For sender-level patterns,
   group by normalized sender and compare multiple messages.
5. Fetch `messages get` with `format=full` only where snippets are insufficient.
   Decode text MIME parts as base64url with their declared charset. Fetch a
   selected `threads get` when prior context changes a summary, reply, or action.
6. Rank urgency only after reading supporting content; report the scope and
   exclusions. Read state is not proof of human engagement.

`has:attachment` also matches calendar invites and `.ics` traffic. Inspect a
sample before concluding that the results represent file sharing. Stale unread
mail alone is not evidence that a sender's newsletters are no longer wanted.
