# Google Cloud

Google Cloud through the `gcloud` CLI, plus the storage substrate this
machine actually uses.

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
```
