---
name: project-intake
description: Gather missing project goal, start/end dates and date certainty, then select appropriate skills and create the canonical project note with actionable tasks. Use before creating a new project or when its scope materially changes.
---

# Project intake

Read `Librarian.md`, the applicable project template, and
`skills/librarian-controller/SKILL.md`. The Librarian owns intake and dispatch.

## Ask for the missing information

Inspect the current request and relevant supplied context first. Reuse facts and
dates already supplied; do not make the user repeat them. Before saving a new active
project, gather the goal (an observable finish line), start date, end date, and
whether the end is a firm deadline or a target. Batch missing questions in one
short exchange. A date can explicitly be undecided; ask rather than inventing one
or silently using today. Confirm “start today” if the start was not already given.

Ask about other template/custom fields only where needed to fill them correctly.
Clarify audience/deliverables or material constraints when they change the skill
selection; infer routine reversible details from the brief and mark assumptions.
Do not force a marketing intake onto unrelated personal, research, or dev projects.

Resolve relative dates from the source date and the user's timezone; state the resulting
calendar dates. Clarify ambiguous dates. Save ISO YYYY-MM-DD dates, or the explicit
value `undecided`, preserving the difference between target and firm deadline.
An end date before the start requires correction before creation. Keep unknown
dates visible rather than confusing them with confirmed dates.

## Select the useful skills

Read available skill names/descriptions in the local catalog and any host skill
catalog exposed in this session. Match actual deliverables, dependencies, and
acceptance checks; do not invoke every role. Start from the controller's roster:
- Evidence gaps: researcher; direction/positioning decisions: strategist.
- Ongoing publishing program: content strategist; a concrete written asset: copywriter.
- Actual draft review: editor; visual/interaction direction: designer.
- Software implementation or fixes: dev; meaningful cross-task coordination: PM.

Select relevant knowledge workflows or host technical/media/document skills only when
the project actually needs them and they are available. Do not invent installed
capabilities or copy every skill into the new project. Librarian-only is a valid
initial plan for work with no specialist need. The planned editor runs after a
draft exists; dev bug fixes do not require copy approval. See the controller for
handoff and authorization boundaries.

Record a short skill plan in the template's marked `para-skills` block: each
selected skill's real path, why it fits THIS project, when it should run, and any
prerequisite. Mark heuristic suggestions as provisional until reviewed. Explain
the choice briefly; the user need not manually staff the team. Skill selection is not
evidence that a skill ran or permission for new external actions.

## Save and follow through

Fill the existing template in place: title, goal, started, due, date_type, skill
plan, and a single actionable task list with acceptance checks/stable IDs. Preserve
custom fields. Explicit `undecided` is a filled answer, not a leaked placeholder.
Use the single-note/promotion rule and `prompts/project-update.md`; maintain one
canonical project and task list. On promotion preserve dates, date certainty,
selected skills, task IDs/completion, user fields, and useful history.

Record the goal/dates as user-reported unless independently checked. Invoke useful
skills only for authorized work required now; retain later-stage selections as a
plan. Reassess that plan when scope or required artifacts change. Preserve deliberate
skill decisions and explain any replacement. Log only when vault writes are in
scope and distinguish selected, invoked, returned, and verified work.

The local New project form enforces explicit date answers and creates initial
specialist suggestions from the brief and tasks. It makes no model call and does
not automatically run agents. The conversational Librarian reviews those suggestions
and selects additional available workflows/tools where relevant.
