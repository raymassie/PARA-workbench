# Project task update

Every new project includes one canonical actionable checkbox list. For a single
project note use its Next steps section; for a promoted project use its README
unless the user has designated another canonical local list or a live tracker. Do not
maintain two live task lists. A designated external tracker remains authoritative;
link it and document any missing button integration rather than creating a shadow
tracker. The local task page handles vault-owned Markdown lists, not external APIs.

## Intake first

New projects follow `skills/project-intake/SKILL.md`. Collect the observable goal,
start date, end date, and end-date type (`deadline`, `target`, or `undecided`).
An explicit undecided answer is allowed; an omitted answer is not. No date is
silently replaced with today. The New project form saves those answers and an
initial skill plan based on the actual brief/actions. This is an editable plan,
not a claim that any specialist has run. The Librarian confirms applicability,
selects additional available host skills when needed, and reassesses on scope change.

## Creating tasks

Write each task as a verb, a concrete deliverable/action, and a clear completion
check: “Test invalid form input and confirm an inline error appears,” rather than
“forms” or “work on site.” Split work that cannot be checked as one observable
action. Include relevant acceptance/review tasks, without inventing extra scope.
Preserve completed items and their evidence. Checking a task records the user's report;
it does not independently prove that a deployment or delivery occurred.

Use the marked block from the project templates. Each task has a stable unique ID;
optional `after:` lists prerequisite IDs from the SAME project:

```markdown
<!-- para-tasks:start -->
- [ ] Implement invalid-input handling <!-- task:implement -->
- [ ] Test invalid input and verify the error appears <!-- task:test after:implement -->
<!-- para-tasks:end -->
```

Keep one checkbox per line and preserve IDs when rewording. Do not put prose,
nested tasks, or a second checklist inside the marked block. Put evidence and
explanation in adjacent notes. Dependencies must exist and must not form a cycle.
Cross-project dependencies are linked in context and reconciled by the Librarian,
not automatically executed by the local task page.

## Check off and Update

Double-click `scripts/project-tasks.command` to open the local task page (Python 3.9+
required), or run `python3 scripts/project-tasks.py --open` from the vault.
The default URL is `http://127.0.0.1:8765/`. The New project form creates a single
note from `templates/project-note.md`, with a finish line and real initial tasks.
On an existing project, check completed actions, add actions as needed, then press
Update. Editing Markdown checkboxes directly also works; press Reload in the task
page before Update so it reads the latest version.

The button executes deterministic local actions:
1. Validate the task IDs, checkbox states, and dependency graph; reject stale edits.
2. Save checkbox states in the canonical Markdown list. Opening a prerequisite
   in the UI also reopens its completed descendants before the save.
3. Recompute progress and next available actions. Set active while work is open,
   ready-for-review when every item is checked, or done only when the user explicitly
   confirms that the project's finish line is met. Reopening work clears that
   confirmation. Custom/paused status requires explicit reconciliation first.
4. Update the existing project status field and marked summary; preserve all
   other content, including Due, decisions, history, and manual sections.
5. Refresh ONLY the Projects listing inside Home's generated Status section;
   preserve the other buckets, Topics, comments, and boundary markers.
6. Append an activity entry and set the project's visible Librarian review flag
   to pending. Save a recoverable before/after journal in `logs/project-tasks/`.

No model/provider is required for these button actions. The page never treats task
text as a command. It does not publish, archive, commit, or start specialist agents.
Those require the Librarian's contextual work and existing action authority.

## Librarian follow-through

At the start of a project session, inspect pending review flags and the activity
record. This is a discoverable handoff, not an automatically running agent job.
For pending updates in scope, compare completed tasks with evidence and the finish
line; reconcile changed decisions, newly unblocked work, other linked projects,
and designated trackers. Use PM and other specialists only where needed.
Perform necessary authorized actions and refresh project summaries/qualifying
indexes using existing workflows. Do not claim a linked-project or external action
occurred merely because a checkbox was checked or a handoff was queued.

Clear the pending flag to `**Librarian review:** reconciled — <date and outcome>`
only after this work is done. Add real follow-up tasks to the canonical list,
preserving IDs/completed history. For a linked project, inspect its current state
and write only within the authorized scope. Record actual checks, affected paths,
and any unresolved blocker. Archive completion still follows archive-sweep's
confirmation rule; done projects remain in place until then.

## Existing notes and promotion

Existing notes without the two marked blocks appear read-only in the task page
with a repair message. Migrate their real canonical actions deliberately; do not
manufacture a second list or silently rewrite an external tracker. On single-note
promotion, move the ONE current task and state blocks to the README, remove them
from the moved source note, and leave a link to the canonical list. Preserve IDs,
checkbox states, evidence, started/due dates, date certainty, skill plan, and user fields. The source note retains
useful historical context; historical checklists must be clearly labeled.

## Recovery and limits

The page serves only on loopback, requires a per-session token for writes, and
refuses stale project versions, nested implementation roots, and archive paths.
Local task saves and report activity appends share `logs/vault-write.lock`.
Keep one active external writer to a note; editor saves do not participate in that lock. Multi-file updates use per-file atomic writes
and a before/after journal; failed saves roll back only matching written content.
If a process dies mid-write, a `.pending.json` journal blocks further writes.
Inspect each recorded before/after value against the current file, complete or
restore only the affected paths without overwriting concurrent edits, then rename
the journal to a resolved extension. No blind reset or automatic retry of writes.
Completed journals retain recovery history and can be archived later.
