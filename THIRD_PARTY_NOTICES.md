# Third-party notices

## First-party license and service marks

First-party source is licensed under MIT; see `LICENSE`. Third-party source
retains its own license and attribution. Service names and trademarks belong
to their respective owners; this integration does not imply their endorsement.
The plugin uses original MIT-licensed symbols rather than copied provider artwork.
See `ICON-SOURCES.md` for artwork provenance.

## OpenAI Gmail component

The upstream Gmail manifest at commit `11c74d6ba24d3a6d48f54a194cd00ef3beea18f9` declares
`author.name: OpenAI` and `license: MIT`:

https://github.com/openai/plugins/blob/11c74d6ba24d3a6d48f54a194cd00ef3beea18f9/plugins/gmail/.codex-plugin/plugin.json

A verbatim copy of that public declaration is preserved in
`licenses/openai-gmail-plugin-manifest.json`. The upstream repository and Gmail
component did not expose a separate LICENSE file at that commit. The standard
MIT license text corresponding to the declaration is retained in
`licenses/openai-gmail-MIT.txt`; it is not represented as a copied upstream
LICENSE file. Preserve OpenAI attribution when updating this component.

OpenAI-authored app registration, vendor skills, references, evaluation cases,
and accompanying assets retain their upstream provenance. Downstream workflows,
helpers, tests, and metadata are maintained by PedroAVJ and use the first-party
MIT license in `LICENSE`.

## Gmail service marks

Google and Gmail names and logos belong to their respective owner. The software
license does not relicense trademarks or imply endorsement. Provider connector
identifiers remain unchanged for compatibility.
