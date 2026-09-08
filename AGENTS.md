# Repository guidance

- This repository is the canonical source for the `google-cloud` plugin.
- Keep the Codex and Claude manifests synchronized when both are present. The Claude plugin is intentionally absent for Codex-only plugins.
- Marketplace catalogs reference this repository; do not duplicate runtime behavior back into a marketplace repository.
- Operator infrastructure maps live outside Git; see `account/README.md` for the optional local path and override. Never commit account maps, tokens, complete API keys, private keys, client secrets, or credential-file contents.
- Preserve stable command names, service labels, and credential identifiers across releases.
- Bump the plugin version for released behavior changes and run `npm test` before publishing.
