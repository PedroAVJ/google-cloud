---
name: gmail
description: Manage Gmail inbox triage, mailbox search, thread summaries, action extraction, reply drafting, and email forwarding through the authenticated Google Workspace CLI (`gws`). Use when the user wants to inspect a mailbox or thread, search email with Gmail query syntax, summarize messages, extract decisions and follow-ups, prepare replies or forwarded messages, or organize messages with explicit confirmation before send, archive, delete, or label actions.
---

# Gmail

## Overview

Use this skill to turn noisy email threads into clear summaries, action lists, and ready-to-send drafts. Prefer Gmail-native search and read workflows, preserve message context, and avoid changing message state without explicit user intent.

## Preferred Deliverables

- Thread briefs that capture the latest status, decisions, open questions, and next actions.
- Reply or forward drafts that are ready to paste, review, or send.
- Inbox triage lists that group messages by urgency or follow-up state.

## Workflow Skills

| Workflow | Skill |
| --- | --- |
| Inbox triage, urgency ranking, and follow-up detection | [../gmail-inbox-triage/SKILL.md](../gmail-inbox-triage/SKILL.md) |

## Reference Notes

| Task | Reference |
| --- | --- |
| Search planning, refinement, pagination, and body-fetch strategy | [references/search-workflow.md](./references/search-workflow.md) |
| Pasted Gmail URL recognition, exact-ID attempts, and fast-fail recovery | [references/pasted-link-workflow.md](./references/pasted-link-workflow.md) |
| Label application, relabeling, and label-based cleanup | [references/label-actions.md](./references/label-actions.md) |
| Self-delivery requests such as "email me," "send this to me," or automation delivery | [references/self-delivery.md](./references/self-delivery.md) |
| Reply drafting, reply-all decisions, and tone matching | [references/reply-workflow.md](./references/reply-workflow.md) |
| Email forwarding, context notes, and intent framing | [references/forward-workflow.md](./references/forward-workflow.md) |

When the user supplies a Gmail web URL, do not pass the URL directly to Gmail tools or turn it into a broad mailbox search. Follow the pasted-link workflow for a bounded exact-ID attempt and immediate recovery guidance when the link cannot be resolved.

## Mailbox Analysis Pattern

For mailbox analysis requests such as triage, follow-up detection, topic summaries, cleanup, thread understanding, or "what matters here" questions, use this pattern:

1. Use `gws gmail users messages list` with Gmail query syntax and a bounded scope. It returns IDs and thread IDs, not summaries; fetch `messages get` with `format=metadata` for sender, subject, dates, labels, and snippets.
2. Read [../gmail-cli/SKILL.md](../gmail-cli/SKILL.md) for exact commands, authentication, MIME handling, drafts, sends, and labels. All Gmail operations use `gws` in both clients.
3. Start with small pages (about 20) and pass `nextPageToken` back as `pageToken` with the same query when more coverage is needed. Never equate an estimated result count with a complete scan.
4. Use `labelIds` as an array of Gmail label IDs, or `q` with `label:NAME`. Resolve custom label names using `users labels list`. Use `includeSpamTrash` when the scope actually includes those folders.
5. Fetch `messages get` with `format=full` only for shortlisted bodies. Use `threads get` with the returned `threadId` when surrounding conversation changes the answer; order its messages by `internalDate`.
6. For broad review without a specified time range, use the previous 24 hours. Exact message/thread requests need no added time window.
7. Summarize before writing when the request is ambiguous. Keep analysis separate from send, archive, trash, or label actions unless the user explicitly asked for them.

## Write Safety

- Preserve exact recipients, subject lines, quoted facts, dates, and links from the source thread unless the user asks to change them.
- When drafting a reply, call out any assumptions, missing context, or information that still needs confirmation.
- Treat send, archive, trash, label, and move operations as explicit actions that require clear user intent.
- If a thread has multiple possible recipients or parallel conversations, identify the intended thread before drafting or acting.
- When supporting context such as policy docs, CRM notes, or Slack history is unavailable, do not foreground that limitation unless it materially changes the recommendation. Prefer a draft grounded in the email thread itself, and mention missing internal context only as a brief confidence note when necessary.

## Output Conventions

- Summaries should lead with the latest status, then list decisions, open questions, and action items.
- Inbox triage should use explicit buckets such as urgent, waiting, and FYI when that helps the user scan quickly.
- When ranking urgency or follow-up state, state the search scope and coverage, such as "from the most recent 15 inbox messages" or "from unread inbox messages matching this query."
- When the task depends on whether the user "opened" or ignored email, treat that as an inference from Gmail read state and do not claim that read state proves human engagement.
- Avoid absolute claims like "the only urgent email" unless the mailbox scan was comprehensive enough to support that conclusion.
- When the result comes from a narrowed search or shortlist, report that confidence and mention what was excluded.
- Draft replies should be concise and ready to paste or send, with greeting, body, and closing when appropriate.
- If a reply depends on missing facts, present a short draft plus a list of unresolved details.
- When multiple emails are involved, reference the sender and timestamp of the message that matters most.
- Avoid repetitive meta-explanations about inaccessible internal sources in normal deliverables. If the user wants provenance, summarize the evidence used; otherwise keep the output focused on the draft, summary, or next action.

## Example Requests

- "Summarize the latest thread with Acme and tell me what I still owe them."
- "Draft a reply that confirms Tuesday works and asks for the final agenda."
- "Go through my unread inbox and group emails into urgent, waiting, and low priority."
- "Prepare a polite follow-up to the recruiter thread if I have not replied yet."

## Light Fallback

If thread or inbox data is missing, say that Gmail access may be unavailable or scoped to the wrong account and inspect `gws auth status` and clarify which mailbox or thread should be used.
