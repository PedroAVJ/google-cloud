# Downstream provenance

The Gmail skills in this repository (formerly `PedroAVJ/gmail`) are a downstream integration of [OpenAI](https://github.com/openai/plugins).

- Upstream baseline at conversion: `11c74d6ba24d3a6d48f54a194cd00ef3beea18f9` (Gmail component, version 0.1.3).
- Upstream source: `https://github.com/openai/plugins.git`.
- Component: `plugins/gmail` in the upstream source.
- Public release history starts from an audited source snapshot. Historical
  private conversion branches, tags, and merge parents must not be republished.
- Upstream copyright and license notices remain intact. See
  `THIRD_PARTY_NOTICES.md` and `licenses/` for license evidence.

## Updating the downstream

Fetch the official upstream into an isolated task clone. Compare the exact
component against the recorded baseline, preserve its attribution, and apply
only reviewed changes to this repository. Keep downstream additions visibly
separate from vendor code. Recheck upstream license declarations for new files.
Do not merge or push an archived private branch as part of an upstream update.

Run the repository tests and plugin validators before publishing. Source,
client installation, and live account behavior are separate verification steps.
