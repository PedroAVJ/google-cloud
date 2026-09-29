# Forward Workflow

Read this file when the user wants to forward an email or thread, decide what context to attach, or turn a long thread into a useful forward.

## CLI path

Use `gws` to read the exact source messages, then compose a new MIME message for
each intended forward. Include the source headers and content below the note,
and preserve the original attachments using the attachment helper. Forwarding
requires explicit send intent; otherwise show a draft in the conversation.
There is no special forward endpoint in the Gmail API. Follow the
[compose reference](../../gmail-cli/references/compose-and-mutations.md).
Do not silently omit attachments or substitute a summary for a requested full
forward. If attachment retrieval fails, report it before sending.

## Core Defaults

- Understand the forwarding intent before adding a note.
- If the user is not clear about why they are forwarding the email, either ask for context you can attach or forward without a note. Do not assume the user's intent.
- Read the message or recent thread context before forwarding so the note, if any, is accurate.
- If the thread is long, summarizing it is often more useful than forwarding without context.
- Be extra careful when forwarding across business email domains. If the recipient is outside the user's company, pay attention to unintentional information exposure and avoid assuming that internal context is safe to share.

## Common Forwarding Intents

- `FYI` -> no action needed
- `Review` -> read and comment
- `Decision` -> approve or reject
- `Action` -> do X by Y

Make the forwarding note explicit about which bucket applies when the user has made that clear.

## Context Note Pattern

1. Identify whether the forward is just a pass-through or whether the recipient needs framing.
2. If framing helps, keep the note short and action-oriented.
3. For long threads, summarize only the parts the new recipient needs:
   - what this is about
   - current status
   - any open question or requested action
   - any deadline or decision needed
4. Match the note to the user's goal and tone.

## When To Ask

- Ask for clarification when the user names the recipient but not the reason for forwarding and the note would otherwise require guessing.
- Ask when the right audience or expected action is ambiguous.
- Do not ask if the user clearly wants a plain forward with no added context.

## When To Send Without A Note

- The user explicitly asks to forward the message as-is, without any added note.
- The forward is truly just for awareness and adding a note would add little value.
- The intent is unclear, but the forwarded content is self-explanatory enough that sending without a note is unlikely to confuse the recipient.
- If the intent is unclear and the forwarded content itself might be confusing, ask the user instead of guessing.
