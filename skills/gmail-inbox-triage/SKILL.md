---
name: gmail-inbox-triage
description: Triage a Gmail inbox into actionable buckets such as urgent, needs reply soon, waiting, and FYI using Gmail data through `gws`. Use when the user asks to triage the inbox, rank what needs attention, find what still needs a reply, or separate important mail from noise.
---

# Gmail Inbox Triage

## Overview

Use this skill for direct inbox-triage requests. Build on the core Gmail skill at [../gmail/SKILL.md](../gmail/SKILL.md), especially its search and thread-reading guidance.

## Workflow

1. Default to `INBOX` and a clear timeframe unless the user asks for a broader audit.
2. Use `gws gmail users messages list` with a bounded query, then `messages get` with `format=metadata` to build a shortlist.
3. Exclude obvious noise early if newsletters, calendar churn, or automated alerts dominate the first pass.
4. Use `messages get` with `format=full` only when snippets are not enough to classify urgency or reply-needed status.
5. Use `gws gmail users threads get` with the returned `threadId` when surrounding conversation changes the classification. Count `messages` and inspect their dates before treating a long notification thread as an active conversation.
6. Return the result in explicit Inbox Zero-style buckets such as `Urgent`, `Needs reply soon`, `Waiting`, and `FYI`.

## Bucket Heuristics

- `Urgent`: direct asks with time pressure, blocking messages, decision requests with deadlines, or operational mail that can break if ignored.
- `Needs reply soon`: direct asks without same-day urgency, active conversations where the user is the next responder, or follow-ups that will go stale if ignored.
- `Waiting`: threads where the user already replied or the current blocker belongs to someone else.
- `FYI`: announcements, newsletters, calendar churn, and transactional mail that does not require action.

## Output

- Include sender, subject, why each item is in its bucket, and the likely next action.
- State timeframe, search scope, and confidence.
- Treat reply-needed as an inference, not a guaranteed state.
- Avoid claiming the inbox is fully triaged if you only checked a narrow slice.
