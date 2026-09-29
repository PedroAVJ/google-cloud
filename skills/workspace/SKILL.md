---
name: workspace
description: Search and manage Google Drive files and Google Calendar events through the authenticated Google Workspace CLI. Use for Drive or Calendar tasks; Gmail uses the dedicated Gmail skills in this plugin.
---

# Google Workspace

Use the installed `gws` CLI. Its Google OAuth grant is separate from Claude account connectors; do not infer that a connected Claude service authorizes `gws`.

Start with `gws auth status`. Never print tokens or credential files. Check the live command schema with `gws schema <service.resource.method>` before unfamiliar calls. Preserve the requested account, calendar, timezone and time window.

## Drive

Search with `gws drive files list --params '<JSON>' --format json`. Use the Drive `q` expression and restrict `fields` to needed metadata. Follow `nextPageToken` only as far as the task needs. Read/download/export the selected file through its exact API method after checking the schema. Do not change sharing or delete files unless requested.

A minimal connection check is:

```sh
gws drive files list --params '{"pageSize":1,"fields":"files(id)"}' --format json
```

## Calendar

Discover calendars with `gws calendar calendarList list --format json`. For a requested interval, use `calendar.events.list` with the selected `calendarId`, RFC3339 `timeMin`/`timeMax`, `singleEvents:true`, and `orderBy:"startTime"`. Follow pagination when required. Check event details and timezone before edits; distinguish an occurrence from its recurring series. Inviting guests or sending updates requires user authorization for that action.

A minimal connection check is:

```sh
gws calendar events list --params '{"calendarId":"primary","maxResults":1}' --format json
```

An `insufficientPermissions` response means the CLI grant lacks a required scope. Explain the missing Calendar permission and use the normal `gws auth login` authorization flow with the existing scopes preserved. Do not remove a working account connector until the replacement has passed a read-only check. Never silently fall back to another user's credentials.

For mutations, inspect the schema, use `--dry-run` when available, perform only the requested change, and read back the result. Creating local draft text does not authorize saving, sharing, emailing, or deleting it.
