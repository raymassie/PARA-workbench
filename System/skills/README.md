# Vault skills

The library contains standard folder-based skills and explicitly loaded Markdown
workflow recipes. Neither is installed globally merely by being in this repository. Read `Librarian.md` and this file first.
PARA's filing rules, sealed archive, and index-only wiki remain authoritative.

## Vault locations

| Purpose | Location |
|---|---|
| Unprocessed captures | `00-raw/` |
| Topic indexes, without original content | `00-wiki/` |
| Completable projects | `01-projects/` |
| Ongoing responsibilities and optional journals | `02-areas/` |
| Reference notes and reusable findings | `03-resources/` |
| Inactive material and sealed processed captures | `04-archive/`, `04-archive/raw/` |
| Cross-vault briefs/reports | `03-resources/compound/` |
| Activity, contradictions, user-supplied theses | `03-resources/vault-log.md`, `03-resources/contradictions.md`, `03-resources/active-theses.md` |
| Operational workflows and local tools | `System/skills/`, `System/scripts/` |

Workflows use this vault's content and supplied context. No personal source vault,
global project tracker, fixed journal collection, or mirrored home-directory tree
is required. Create optional notes only when actual content needs them.

## Shared conventions

- Use the actual local date. For recent windows, use explicit note dates,
  `git log --since=... --name-only`, and current uncommitted changes together.
  Respect the parent/nested repository ownership boundaries in `Librarian.md`;
  exclude implementation trees from evidence searches. Do not treat filesystem modification dates after sync/clone as evidence of activity.
- Read the topic indexes and the latest entries at the END of
  `03-resources/vault-log.md` before working. If no entries exist, say so.
- Exclude operational docs, templates, logs, and previous generated compound
  reports as evidence of the user's beliefs or recurring patterns. Follow their cited
  sources instead. Archived source captures may be read, never edited.
- Generated outputs use `created`, `tags`, and `sources` frontmatter, with sources
  linking to the actual notes used. One canonical report per date/type (weekly:
  ISO week). Read an existing output before refreshing it; preserve manual additions.
- File reports under `03-resources/compound/YYYY-MM-DD-<type>.md`; weekly reports
  use `03-resources/compound/weekly/YYYY-Www.md`. Lint uses
  `03-resources/compound/lint/YYYY-MM-DD.md`.
- Index reports when their topic spans at least two notes, following translate's
  existing threshold. Do not create a resource-folder README or put substance in
  `00-wiki`. Refresh Home after a manual operation changes its listing.
- Append completed manual operations to `03-resources/vault-log.md`, naming
  affected paths, findings, and limitations. Runtime stdout/stderr belongs in
  `System/logs/`, never in the topic index.
- Use `System/skills/vault-transaction.md` for ingest, multi-source merges, authorized
  audit fixes, or edits to three or more existing files. Read-only analyses need
  no checkpoint. Never edit raw/archive sources or import another vault’s note collection.
- Imported workflows do not install schedules or authorize calendar writes,
  research, publishing, or changes to the user's theses.

## Project intake

`System/skills/project-intake/SKILL.md` gathers missing goal/start/end-date answers and
selects the minimum useful skills for each new project. Dates may explicitly be
undecided; firm deadlines and targets remain distinct. The skill plan stays with
the canonical project and is preserved through promotion.

## Librarian and specialist agents

Read `System/skills/librarian-controller/SKILL.md` for the eight-role roster, dispatch and
return contract, provenance, ownership, integration checks, and logging. The role
definitions live in `System/skills/content-strategist/`, `System/skills/copywriter/`,
`System/skills/designer/`, `System/skills/dev/`, `System/skills/editor/`, `System/skills/pm/`,
`System/skills/researcher/`, and `System/skills/strategist/`, each with one `SKILL.md`.
These optional specialists are selected by task; there is no mandatory marketing
chain. Read role files as needed; native discovery varies by assistant. Librarian.md
is still the canonical vault policy. Specialist skill instructions are subordinate
to it and do not expand action authorization. Shared report conventions above
apply to compound reports; project deliverables follow the controller's PARA rules.

## Skill packaging

Standard Agent Skills use one folder per skill with a `SKILL.md` containing name,
description, and instructions. Scripts/references/assets are optional, included
only when needed. The specialists, controller, and intake use this layout. The
knowledge workflow files below are explicit-load Markdown recipes, not installed global skills.
The vault’s `System/skills/` library is reached from Librarian.md; host-native automatic
discovery may require a host-supported location or installation. A folder alone
does not install a skill or grant tools. Avoid duplicating the canonical files.

## Knowledge workflow recipes

Use these phrases with the Librarian. Load only the matching file; the whole
library is not a mandatory sequence. The workflows are on-demand.

| Ask for | Purpose | Required context/setup | Workflow |
|---|---|---|---|
| Verify a filed capture | Source comparison, Librarian acceptance and optional read-only checks | Actual source, saved output and pre-state | `System/skills/capture-acceptance.md` |
| Morning brief | Priorities, open loops, next actions | Existing notes; calendar is optional | `System/skills/morning-brief.md` |
| Calendar sync | Reconcile schedule and intentions | An authorized calendar source or optional local calendar configuration | `System/skills/calendar-sync.md` |
| Find connections | Non-obvious relationships in filed notes | Related substantive notes | `System/skills/connection-finder.md` |
| Surface patterns / Spark | Recurring concerns across recent material | Dated notes/captures | `System/skills/pattern-surfacing.md` |
| Track beliefs | Supporting/challenging evidence for stated theses | Optional owner-supplied theses; no beliefs are inferred | `System/skills/belief-tracker.md` |
| Weekly synthesis | Themes, tensions, and open questions | Recent source material | `System/prompts/weekly-synthesis.md` |
| Refresh project status | Reconcile local project records and Home within scope | Current canonical project notes; write authorization | `System/prompts/project-review.md` |
| Review my projects | Coherence, evidence, dependencies, missing information | Relevant canonical project notes | `System/prompts/project-review.md` |
| Check vault health | Structural/link/schema findings | Read access; no automatic fixes | `System/prompts/audit.md` |
| Help customize my vault | Guided owner preferences | Optional local profile; skipping fields is allowed | `System/prompts/setup.md` |

`System/skills/claim-ledger.md` supports source-claim comparison during substantive ingest
and synthesis; `System/skills/vault-transaction.md` supports scoped bulk changes.
`System/skills/vault-prompts.md` contains reusable question, writing, and decision prompts.
These support workflows when triggered, not a team to run on every question.
See `System/scripts/README.md` for optional report runners, calendar helper, and local tools.
