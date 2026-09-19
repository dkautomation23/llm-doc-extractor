# Security policy

llm-doc-extractor reads a document and a field schema, and asks a chosen LLM
provider (or a no-key `demo` mode) to return matching JSON. This file defines
what counts as a security issue in that specific tool.

## Reporting

Use GitHub's private vulnerability reporting on this repository: **Security →
Report a vulnerability**. It opens a private thread; nothing becomes public
until there is a fix.

If that is not available to you, email **hello@dkautomation.dev** with
`llm-doc-extractor` in the subject line.

Include the commit or version you ran, the exact command, and what happened.
A proof of concept is welcome; a scanner's raw output usually is not.

**Do not open a public issue for a vulnerability.**

## Supported versions

No tagged releases yet — the `main` branch is the supported version. Report
against the commit you actually ran.

## What to expect

| | |
|---|---|
| First reply | within 3 working days |
| Assessment | within 7 working days of the first reply |
| Fix or a stated decision not to fix | within 30 days for anything reproducible |

Single-person commitments, not a company SLA.

## Scope

The document given with `--doc` is often someone else's file (an invoice, a
contract) — treat its content as untrusted. The schema given with `--schema`
is normally your own, but its field `description` text is also placed into
the model prompt verbatim, so it is worth the same caution.

In scope:

- Content inside the document, or inside a schema field's `description`,
  that changes what the tool **does** rather than what it extracts — in
  particular, makes it read, write, or send a file other than the ones
  named on the command line (`--doc`, `--schema`, `--out`).
- The document or schema causing `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`, or
  their values, to appear in output, logs, or a request to a host other than
  the selected provider's own API.
- `--provider ollama` being made to reach a host other than the local Ollama
  endpoint it is hard-coded to call.

Out of scope:

- The model returning a wrong or hallucinated field value — an accuracy
  problem with the provider/model you chose, not a vulnerability here.
- The `demo` provider's rule-based extractor missing a field it was never
  designed to parse (it has no model behind it).
- PDF text-extraction quality — that is `pypdf`'s behaviour, not this
  repository's.

## Credit

Named in the fix's release notes if you want that; say so if you would rather
not be.

There is no bug bounty.
