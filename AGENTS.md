# Repository guidance

- This repository is the canonical source for the `google-cloud` plugin.
- Keep the Codex and Claude manifests synchronized when both are present. The Claude plugin is intentionally absent for Codex-only plugins.
- Marketplace catalogs reference this repository; do not duplicate runtime behavior back into a marketplace repository.
- Operator infrastructure maps live outside Git; see `account/README.md` for the optional local path and override. Never commit account maps, tokens, complete API keys, private keys, client secrets, or credential-file contents.
- Preserve stable command names (`ytx`, `gmail-attention`), service labels, connector identifiers, and credential identifiers across releases: the `gws` client at `~/.config/gws/client_secret.json`, the `ytx-oauth` Keychain token, and `~/.config/ytx/`.
- The Gmail skills are a downstream of OpenAI's `openai/plugins` Gmail component. Preserve OpenAI attribution and license evidence (`GMAIL-DOWNSTREAM.md`, `THIRD_PARTY_NOTICES.md`, `licenses/`), and keep OpenAI-authored files distinguishable from downstream additions.
- Bump the plugin version for released behavior changes and run `npm test` before publishing.
