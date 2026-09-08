# Local infrastructure context

Account and infrastructure maps belong outside the plugin repository. The
optional default is `~/.config/google-cloud-plugin/infrastructure.md`;
`GOOGLE_CLOUD_INFRASTRUCTURE_FILE` may select another private local Markdown file.
Do not copy an operator map into this directory or into a plugin cache.

Use the map only as context and verify relevant project purpose, resource
ownership, IAM, and safety boundaries with live `gcloud` reads. If no map exists,
discover the intended project from the current task and authenticated account.
Ask only when live evidence cannot resolve an ambiguity. A map never authorizes
writes or proves the current state of a resource.

A local map can use `Projects`, `Buckets`, and `API keys` headings, with purposes
and ownership notes. Never include key values, tokens, secrets, or credential-file
contents. Restrict the file to its owner and keep its contents out of public logs.
