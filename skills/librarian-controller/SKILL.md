---
name: librarian-controller
description: Coordinate PARA-workbench work using content strategist, copywriter, designer, dev, editor, PM, researcher, and strategist specialists when needed. Use for specialist delegation and integration; handle routine vault filing directly.
---

# Librarian controller

Read `Librarian.md` and `README.md` at the vault root. This is the canonical
delegation protocol; specialist skills reference it rather than duplicating it.
The Librarian remains the user's front door and owns task scope, routing, coordination,
integration, PARA placement, and the final verified answer. PM is a specialist,
not a second controller. Use only the roles the task needs.

These maintained local definitions are self-contained. No source checkout,
personal vault, or home-directory layout is required at runtime.

## Roster and routing

| Specialist | Load | Delegate when | Return |
|---|---|---|---|
| Content strategist | [skill](../content-strategist/SKILL.md) | Ongoing editorial program, cadence, repurposing | Feasible content plan |
| Copywriter | [skill](../copywriter/SKILL.md) | A specific piece needs words | Draft and claims/proof notes |
| Designer | [skill](../designer/SKILL.md) | Visual direction, layout, interaction or design critique | Direction/handoff and measured checks |
| Dev | [skill](../dev/SKILL.md) | Build, fix, integrate, instrument | Implemented change and verification evidence |
| Editor | [skill](../editor/SKILL.md) | Draft needs truth, clarity, voice, or release review | READY, REVISE, or BLOCKED with reasons |
| PM | [skill](../pm/SKILL.md) | Several dependencies, sequencing, ownership or delivery uncertainty | Dependency/coordination update |
| Researcher | [skill](../researcher/SKILL.md) | A question or consequential claim needs evidence | Findings with sources and gaps |
| Strategist | [skill](../strategist/SKILL.md) | Direction, audience, positioning or a material tradeoff | Recommendation, alternatives and proof obligations |

Start from the requested outcome and inspect existing context before dispatch.
Reuse relevant project notes, current decisions, designated live trackers, and
source documents. Read only relevant role skills. Routine translate, audit, or
Home refresh does not need a team. Missing evidence routes to researcher;
unresolved direction routes to strategist. PM is useful for coordinating a real
dependency graph, not as a mandatory intake step.

For marketing copy, use existing positioning or a sufficient explicit brief. If a
material audience/offer/claim decision is missing, fill that gap first. Content
strategist and designer can work alongside copywriter after the shared brief is
stable; editor reviews the completed draft before release readiness. Dev consumes
approved public copy for a marketing build, but may fix a bug or implement an
unrelated tool without a marketing plan, positioning document, or copy verdict.
Research questions do not require competitor URLs. Do not require unconfigured roles or a fixed marketing pipeline as prerequisites
for unrelated work.

New project creation first follows `skills/project-intake/SKILL.md`: collect
missing goal/date answers and select relevant available skills with reasons and
invocation stages. Retain that plan in the canonical project and reassess it for
material scope changes. Selection does not mean invocation. Task changes follow
`prompts/project-update.md`. Keep
one actionable checkbox list, preserve it through promotion, and inspect pending
Librarian review flags before project work. The task page computes local status
and Home changes; the Librarian owns contextual linked-project and specialist
follow-through within scope, and clears the flag only after completing that work.

Use `prompts/project-review.md` for project coherence and material knowledge gaps.
This is a Librarian check, not a new mandatory specialist. Reuse answers and ask
only the material missing questions, while continuing independent authorized work.

## Dispatch and return contract

Give each specialist a bounded handoff with these fields (in the task message;
persist only when useful for a longer project):

```text
Role and task ID:
Requested outcome / concrete deliverable:
Context: relevant paths or supplied excerpts, source dates, current decisions
Known facts / inferences / assumptions / open questions:
Dependencies: accepted input and the version being used
Permitted tools, exact write paths (or return-only), and actions already authorized:
Acceptance checks and expected return format:
```

Return: completed work or a proposed patch, source/evidence references, exact paths
changed (if any), verification performed and results, remaining assumptions,
blockers, and the next dependency. A route or a plan alone is not task completion.

Use the host's actual subagent/delegation facility when available. Give independent
read-only work parallel tasks where useful; serialize dependent tasks. Default to
return-only specialists and let the Librarian apply shared-note changes. Assign
exclusive, non-overlapping write paths for authorized implementation workers; no
two agents edit the same file at once. Workers request a scope change through the
Librarian instead of recruiting more agents or widening their own permissions.
If native delegation is unavailable, do the roles sequentially in the same session
with explicit role handoffs. State that it was a role pass, not a separately run
agent. These files alone do not create processes, install plugins, or grant tools.

On return, inspect the output and evidence, reconcile conflicts, apply accepted
changes, and run checks appropriate to the result. The Librarian owns follow-through
until the authorized outcome is done or a specific blocker remains. Route failed
checks back to the responsible specialist. Use at most three editorial revision
rounds; a repeated failure of the same criterion twice should expose the missing
premise rather than trigger endless rewrites. Continue independent work while a
real external decision/access blocker is pending.

## Evidence and decision authority

Preserve evidence markers in working notes and handoffs:
`[confirmed]` with a named source/date and whether user-reported or directly checked;
`[inferred: from ...]`; `[assumed: ...]` with what would resolve it. A source saying
something confirms that it said it, not that the statement is universally true.
Never strip an assumption marker between roles. The claim-ledger markers
describe agreement/contradiction; these describe evidence status. Use both when
applicable, without treating corroboration as proof of truth.

Editorial checks use [rubrics](references/rubrics.md) when the asset type fits.
[Role heuristics](references/role-heuristics.md) support strategist, copywriter,
editor, researcher, and PM; load the relevant section, not every reference.
Keep production copy clean; evidence markers and proof notes live in an adjacent
working section or existing evidence note, with a clear connection to each claim.

The Librarian resolves routine implementation choices. The user retains material goal,
budget, publication, and irreversible-action decisions outside existing authority.
Any specialist can report a blocker. An editor's READY verdict means quality
readiness, not permission to publish, deploy, send messages, spend, or commit.
Neither PM nor the Librarian may relabel an unresolved factual blocker as passed.
Reuse existing authorization; do not repeatedly ask for permission already given.

## Persistence, boundaries, and logging

Use the current project/area note or its promoted folder for project-specific
briefs, positioning, content, copy, design direction, and review evidence. Preserve
the single-note-to-folder promotion rule; do not create empty context/status files
or force a folder for every role. General reusable findings go to `03-resources`.
Use `00-wiki` only to index qualifying topics. Keep raw/archive sources unchanged.
Never put project deliverables in the operational `skills/` directory.

PM updates an existing coordination/current-state section with accepted artifacts,
role ownership, dependency state, unresolved decisions, and evidence links. Keep
one canonical next-actions list or designated live tracker; do not create another
`status.md`, `context.md`, or root-level role tracker by default. Preserve useful
history via linked evidence or an archive before superseding it.

Implementation work stays in its project repository and respects parent/nested
ownership rules. Use `skills/vault-transaction.md` where triggered. Delegation
inherits the user's scope; it does not authorize extra research or external writes.
The existing report-only runners retain their restrictions and cannot dispatch
write-enabled specialists. Any fallback within them must remain report-only.

After a substantive multi-role operation, when vault writes are authorized, append
its result to `03-resources/vault-log.md`: task/outcome, roles actually used, native delegation
or sequential passes, affected paths, checks/results, and unresolved blockers.
Read-only tasks return inline and do not save artifacts or append a log. Code-only
write authorization does not grant vault-note writes; return relevant status evidence
to the Librarian without editing those notes unless that work is also authorized.
Log completed evidence, not a claim that work continues after the session ends.
Use the existing runtime logs only for actual script runs. In the final reply,
state the result, material limits, and where the canonical artifact lives.
