# Self-Delivery

Use when the user explicitly asks to email content to their own Gmail account.

1. Read `gws gmail users getProfile --params '{"userId":"me"}'` and use its
   `emailAddress` as the recipient. `me` is an API user ID alias, not an email
   address to put in MIME headers.
2. Compose the requested content using the
   [compose reference](../../gmail-cli/references/compose-and-mutations.md),
   omitting Cc and Bcc unless the user requested them.
3. An explicit "email me" request authorizes sending to that account; do not
   ask again merely because the body was generated during this turn. A request
   to draft remains unsent. Verify the API returned a message ID before claiming
   success, and never automatically retry an uncertain send.
