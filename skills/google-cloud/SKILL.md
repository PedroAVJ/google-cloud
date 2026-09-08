---
name: google-cloud
description: Work with Google Cloud through the gcloud CLI — discovering which projects exist and what each is for, authentication, project scoping, cost-aware querying, and the safety boundary around production resources. Use for any GCP task — inspecting or provisioning resources, checking logs, auditing IAM, or figuring out which project something lives in. For Cloud Storage specifically, see the storage skill.
---

# Google Cloud

`gcloud` is the interface. It is a wrapper over the Google Cloud REST APIs
and exposes effectively the whole surface — every service, every flag. That
makes it strictly more capable than any MCP server or connector fronting the
same platform, because those expose a curated subset chosen as a product
decision, not a technical ceiling. Shell out to `gcloud`. Do not install an
MCP server to reach Google Cloud.

```bash
gcloud version
gcloud auth list
gcloud config list
```

## Projects

Getting the project wrong is the most common and most expensive mistake here.
Name it explicitly on every command rather than relying on ambient
`gcloud config` state.

Project IDs are opaque and permanent — they are auto-generated at creation and
frequently say nothing about what the project ended up carrying. **Never infer
a project's purpose from its ID or display name.** Discover it:

```bash
gcloud projects list --format="table(projectId,name,projectNumber)"
gcloud services list --enabled --project=<project> --format="value(config.name)"
gcloud storage ls --project=<project>
gcloud iam service-accounts list --project=<project> --format="value(email)"
```

Read the optional private local infrastructure map described in
[`../../account/README.md`](../../account/README.md): resolve
`GOOGLE_CLOUD_INFRASTRUCTURE_FILE`, or use
`~/.config/google-cloud-plugin/infrastructure.md` when the override is unset.
If the file exists, use its project purposes and known safety boundaries as
context; if absent, use live discovery and the current request. Verify the
relevant live state with the commands above because a local map can drift. If purpose is still unclear, ask rather than
assume—and never treat a project as disposable because its name looks like a
demo or experiment.

Projects are free, so a tidy-looking consolidation is rarely worth it. Merging
is a real migration: bucket names and their parent project are permanent, OAuth
clients and API keys cannot move, and one consent screen per project means
merging entangles unrelated apps' verification state.

## Authentication

The Google Cloud CLI and local application libraries use separate credential
stores:

- **gcloud CLI credentials** — direct `gcloud` commands use the active account
  shown by `gcloud auth list`. For the user's interactive local work, sign in with
  `gcloud auth login` when no suitable account is active.
- **Application Default Credentials (ADC)** — Google client libraries use ADC,
  not the CLI's active-account store. Set up local user ADC with
  `gcloud auth application-default login` only when an application library
  needs it; native `gcloud` work does not.

Deployed workloads should use their platform identity. Never copy a service
account key onto this machine merely to make local work succeed.

Where a personal GCP project with a published OAuth client already exists,
adding a new Google API is *enable API → add scope → re-consent*, not a new
project. Keep the consent screen's app name meaningful — it is what appears in
the account's third-party access list.

```bash
gcloud auth list --filter="status:ACTIVE" --format="value(account)"
gcloud services list --enabled --project=<project>
```

Never print an access token, key material, or a service-account JSON into the
transcript.

## Scoping Every Command

Ambient config is a trap when several projects exist. Prefer explicit flags:

```bash
gcloud <group> <command> --project=<project> --format=json
```

Use `--format` to cut output rather than piping large JSON through context:

```bash
gcloud projects list --format="value(projectId)"
gcloud storage ls --project=<p> --format="value(name)"
gcloud logging read 'severity>=ERROR' --project=<p> --limit=20 --format=json
```

Prefer `--limit`, `--filter`, and `--format=value(...)` on anything that could
return an unbounded list. A `gcloud logging read` without `--limit` can return
enormous output.

## Safety Boundary

Read freely. Before any command that creates, modifies, deletes, or spends:

1. State the project and the exact resource.
2. Use `--dry-run` where the command supports it.
3. Get an explicit yes.

Never run without asking first:

- `gcloud projects delete`, `gcloud storage rm`, `gcloud sql instances delete`,
  or any other delete against a resource holding data
- IAM grants that widen access (`add-iam-policy-binding` with broad principals
  like `allUsers` or `allAuthenticatedUsers`)
- Anything that changes billing, quota, or org policy
- Anything touching a live client system's production resources, or any
  bucket holding backups — treat backups as the only irreplaceable data
  present until proven otherwise

Treat `gcloud` as capable of real destruction, because it is. The CLI's
breadth is the reason to prefer it and the reason to gate it.

## Provisioning

Creating resources is in scope when asked. Keep new resources inside the
project already serving that purpose unless there is a reason not to, name
them for what they serve, and state the ongoing cost before creating anything
billable.

For buckets specifically, follow the naming and prefix conventions in the
`storage` skill rather than inventing a layout.

## Reference

Google publishes exhaustive official skills for individual services
(`google/skills` on GitHub, e.g. `google-cloud-storage-basics`, `gke-*`,
`bigquery-*`). Read them upstream for deep per-service surface. Do not vendor
them into this repo and do not install them as standalone skills — Apps ships
application integrations as plugins only.
