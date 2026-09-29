# Google Cloud

Google through its command-line interfaces: Google Cloud through `gcloud`,
Google Workspace (Gmail, Drive, Docs, Sheets, Calendar, Tasks, People) through
the Google Workspace CLI `gws`, Gmail workflows, and YouTube
through the plugin-owned `ytx` CLI.

This plugin absorbed the former `gmail` and `youtube` plugins. Their skills,
CLIs, scripts, and references now live here; credential, token, and cache
identities are unchanged.

## Why The CLI, Not An MCP Server

`gcloud` is a wrapper over the Google Cloud REST APIs and exposes effectively
the entire surface. An MCP server fronting the same platform exposes a curated
subset — a product decision, not a technical ceiling. So reaching Google Cloud
through MCP is strictly *less* capability at the cost of extra context for
tool schemas.

Google does ship an official MCP server ([`googleapis/gcloud-mcp`](https://github.com/googleapis/gcloud-mcp),
in preview, not covered by Google Cloud ToS) and official per-service skills
(`google/skills`). Neither is installed here. The rule in this repo is
CLI + skill, and MCP only when no callable interface exists — `gcloud` is
callable, so it wins.

## Skills

| Skill | Use it when |
| --- | --- |
| `google-cloud` | Any GCP task: which project a thing lives in, auth, scoping commands, provisioning, and the safety boundary around production resources. |
| `storage` | Which bucket holds what, the repo-scoped prefix convention, and how to identify read-only backup and application buckets. |
| `publish` | Turning a local file into a durable URL with native `gcloud storage` commands, including deciding whether it belongs in Cloud Storage or Google Drive at all. |
| `gmail` | Gmail through `gws`: search, thread summaries, drafting, forwarding, labels, self-delivery, pasted links. |
| `gmail-inbox-triage` | OpenAI's inbox triage into urgent, needs reply soon, waiting, and FYI. |
| `gmail-cli` | Gmail API metadata, MIME source, attachments, and compose/label operations through `gws`. |
| `gmail-review-attention` | Stateless, received-time-bounded review of consequential inbound Gmail. |
| `gmail-review-inbox-hygiene` | Read-only unwanted-message review with manual unsubscribe, block, or report suggestions. |
| `youtube` | Playlists, liked videos, subscriptions, and quota through `ytx` over the YouTube Data API v3. |

## Gmail

Codex and Claude Code use the authenticated Google Workspace CLI `gws` for
all Gmail operations. The optional curated Gmail plugin is not required, and
this plugin registers no Gmail app connector. Keep `gws` authenticated with the
Gmail API enabled for its OAuth project. Draft text stays in the conversation
unless the user asks to save a Gmail draft; sending requires send authorization.

```bash
gws auth status
gmail-attention scan                 # previous 24 hours of received mail
gmail-attention scan --since 48h
```

The scanner is stateless and never mutates Gmail. See
[`GMAIL-DOWNSTREAM.md`](GMAIL-DOWNSTREAM.md) for OpenAI upstream provenance
and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for licensing.

## YouTube

`ytx` is a single stdlib-only Python file at
[`scripts/youtube_cli.py`](./scripts/youtube_cli.py). It reuses the Desktop
OAuth client configured for `gws` (`~/.config/gws/client_secret.json`) but
keeps its own token in the macOS Keychain (`ytx-oauth`) and its SQLite mirror
at `~/.config/ytx/cache.db`. Quota is 10,000 units/day; `ytx quota` reports
today's spend. See
[`limitations.md`](./skills/youtube/references/limitations.md).

```bash
ytx auth status
ytx playlists list
ytx sync && ytx playlists list --cached
```

## The Substrate

Buckets in one project typically serve unrelated jobs — published artifacts,
backups, live application media — and only the first is ever agent-writable.

The write boundary is the reason this plugin exists. The buckets look
interchangeable and are not. Read the private
map configured as described in [`account/README.md`](account/README.md) before operating
the user's account, then verify the relevant live state with `gcloud` because
cloud configuration can change.

## Publishing

The plugin does not ship a custom publishing command. The `publish` skill uses
the installed Google Cloud CLI directly: discover the exact project and bucket,
then run `gcloud storage` for inspection and uploads.

```bash
npm test
```

## Install

```bash
claude plugin install google-cloud@package-manager
```

```bash
codex plugin add google-cloud@package-manager
mkdir -p ~/.local/bin
ln -sfn ~/.codex/plugins/cache/package-manager/google-cloud/<version>/bin/ytx ~/.local/bin/ytx
ln -sfn ~/.codex/plugins/cache/package-manager/google-cloud/<version>/bin/gmail-attention ~/.local/bin/gmail-attention
```

The plugin-owned wrappers are stable front doors into the released plugin
cache. Repoint the versioned symlinks only after the replacement release is
installed and verified.
