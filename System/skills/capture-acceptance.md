# Capture acceptance

Trigger: translating a capture, reviewing an agent's filed submission, or checking
an authorized maintenance ingest. Read the translate and vault-transaction recipes.
The Librarian coordinates the work and owns final acceptance. A single assistant
can produce and then review in a distinct pass; a fixed agent team is optional.

## Review and continue

1. Before mutation, read the actual raw capture and every merge target in full.
   Preserve the transaction's before-state outside live notes. Inventory each
   idea and its source sections, meaningful examples, qualifications and tables.
   For PDF/image tables, inspect the rendered source when extraction is ambiguous;
   account for every substantive column and cell, including units, row labels,
   footnotes and relationships. Unavailable source access is a specific blocker.
2. File through translate's existing rules. Preserve prior notes and attribution;
   compare claims through the claim-ledger recipe. Keep every raw byte unchanged,
   including metadata. A new note can remain a single file and a lone note needs
   no topic index. Preserve project/area promotion rules and the two-note index
   threshold. A task, unreadable capture or unresolved idea stays in `00-raw`.
3. Review the saved output against the source and before-state in a distinct pass.
   For a multi-source merge, read each source's contribution in context and retain
   its qualifications, attribution, uncertainty and contradictory claims. For
   substantive or difficult submissions, use an independent checker when available;
   the Librarian must still inspect its evidence and confirm the submission.
   Identify who actually checked it; self-review is the minimum when working alone.
4. Verify destination links, justified indexes, collision-safe original move and
   Home's actual bucket inventory and preserved manual sections. The optional
   helper below supports mechanical checks. Inspect claim/contradiction records
   and the required activity entry separately; the helper does not check them.
5. In the operation's existing activity/status record, identify reviewed paths and
   versions/hashes, checks actually performed, semantic/source evidence, remaining
   issues, reviewer and final **PASS / REVISE / BLOCKED**. Separate the helper's
   mechanical result from the Librarian's full acceptance. Repair authorized
   failures and recheck changed output. Record exact blocked items and continue
   independent work. Do not make development logs or sample notes in this starter.
6. After acceptance, execute the next eligible capture or repair already authorized
   in the bounded batch. A completed internal stage does not require another
   “proceed.” Stop at the requested endpoint, explicit limit, unavailable access or
   an actual decision/approval dependency; save the next action if work remains.

## Optional read-only helper

Python 3.9+; stdlib only, no Git, account, configuration, model or scheduler:

```sh
python3 -B System/scripts/check-capture.py --vault /path/to/vault --manifest /path/to/capture.json
```

It reads files and prints JSON to stdout. Exit codes: `0` mechanical PASS, `1`
REVISE, `2` BLOCKED. It never files, tags, archives, refreshes Home, writes a report
or grants filing authority. Store a real manifest with the operation's existing
external before-state records; it can contain private source text. Each invocation
checks one capture against its immediate pre-move archive inventory. Retake the
inventory before the next capture; coordinate shared mutations under the existing
workflow lock rather than treating this read-only helper as a lock.

Prepare the manifest from actual pre-state **before** changing files. Schema 1:

| Field | Required declaration |
|---|---|
| `schema_version` | `1` |
| `capture.original_path`, `sha256` | Canonical vault-relative `00-raw/...` path and lowercase SHA-256 of the complete original file bytes |
| `capture.state` | `archived`, `task`, `unreadable` or `unresolved` |
| Archived capture | `archive_path`: dated collision-safe `04-archive/raw/YYYY-MM-DD-name`; `archive_before`: object mapping **every** prior raw-archive file path to its whole-file SHA-256 |
| Retained capture | `reason`: exact blocker/task; omit `archive_path`; original must remain at its original path |
| `ideas` | Nonempty list of objects: unique `id`; `state`: `filed`, `skipped` or `flagged`; filed ideas have a nonempty `destinations` list; other states have `reason` and no destinations |
| `expected_coverage` | Complete source-review inventory of unique unit IDs, including each meaningful table column; empty only when nothing is filed |
| `coverage` | One object per expected ID: `id`, `idea_id`, `kind` (`text` or `table_column`), `destination`, and literal `evidence_text` found in that filed note |
| `preserved_files` | List of unchanged-file objects with `path` and pre-state `sha256`; include protected affected material outside the raw archive |
| `existing_notes` | List of merged-note objects with `path`, full UTF-8 `before_text` and its `before_sha256`; empty for all-new notes |
| `indexes` | List of relevant index objects with `path` under `00-wiki` and ≥2 distinct `qualifying_notes` linked by unambiguous vault-path wikilinks; empty when no index is justified |
| `home` | Object with full UTF-8 `before_text`, its `before_sha256`, existing `generated_start` and `generated_end` delimiters, `expected_links` and `refresh_checked: true` after actual inventory review |

All list fields are required; use `[]` for none. Paths are relative to the vault,
canonical, and symlink-free. Filed destinations belong in substance buckets,
including the appropriate archived bucket for inactive work. A flagged idea
prevents archiving the original. Archived raw neighbors must match pre-state and
the only new raw-archive path may be this capture's new destination.

For Home, `before_text` and `before_sha256` describe the immediate pre-digest
baseline **after** separately reviewed, authorized Topics additions. Retain the
original operation baseline separately: compare each approved Topics edit against
it and verify that every other manual section is preserved. The helper checks the
subsequent digest against that immediate baseline; it does not approve Topics edits.

For the shipped Home, delimiters are `"## Status\n"` and
`"<!-- Generated by System/prompts/home-digest.md"`; inspect the actual Home before
using them. The helper preserves everything through the start delimiter and from
the end delimiter onward. `expected_links` are the reviewed generated listing's
relative Markdown targets, including files or real folder entry points. Correct
listing and completeness of that list still require the Librarian's review.
Existing-note checks conservatively require the full prior text as a contiguous
substring. A legitimate reorganized merge therefore needs manual inspection;
a helper REVISE must be explained, never silently relabeled PASS.

## What the result establishes

A mechanical PASS verifies only the declared hashes, dispositions, literal evidence
fragments, links and boundaries. It **cannot discover an omitted source idea or
column omitted from both inventories**. A header match cannot establish that its
cells or their meaning survived. Check every substantive cell/column against the
source and saved note, independently of the helper. Pre-state declarations are
caller-supplied evidence, not authenticated history; preserve the originals and
inspect those declarations. Recheck final hashes after repairs.

Semantic completeness, classification, relevance, claim/ledger consistency,
activity accuracy, authorization and independent review remain outside this tool.
The JSON explicitly marks its limits UNVERIFIED. A complete filing decision needs
the Librarian's source comparison and workflow checks above. For an unsupported
file shape or failed check, preserve the source, state the precise limitation,
and follow the existing transaction recovery procedure before accepting work.
