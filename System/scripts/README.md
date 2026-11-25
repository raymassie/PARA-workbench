# Runners, schedules, and logging

## Local project task page

Double-click `project-tasks.command` or run `python3 System/scripts/project-tasks.py --open`
from the vault root. It starts a local Python 3.9+ server at `http://127.0.0.1:8765/`
and opens the task page. Leave the launcher running while using it; stop it with
Ctrl+C. If already running, open the printed address instead of launching a second
copy. There is no installed background service. Optional `--port` and `--vault`
arguments support alternate local/test configurations; note links use default port.

`project-tasks-ui.html` is the local interface; `project-tasks.py` reads/writes the
canonical Markdown task blocks and only the project status/summary, Home's
generated Projects line, and the append-only activity log. Existing notes without
managed blocks appear read-only for deliberate migration. `System/logs/project-tasks/`
retains before/after recovery journals and a shared writer lock at `System/logs/vault-write.lock`, ignored by Git. A pending
journal blocks further writes until it is inspected and resolved. See
`System/prompts/project-update.md` for the protocol and recovery steps.

New project creation uses the actual project-note template. It requires explicit
start/end-date answers (or an explicit undecided choice), distinguishes deadlines
from targets, and rejects an end before the start. Initial specialist suggestions
are generated locally from the goal/actions and recorded with reasons and stages;
the Librarian reviews them before dispatch and considers other available skills. Templates with extra
custom placeholders require Librarian input; the form will not invent their values.
Update does not call an AI model. Pending contextual agent/cross-project follow-up
is shown in the project and handled in the next Librarian session.

The report runner and task updater share `System/logs/vault-write.lock` around activity
writes, preventing those tools from losing each other’s log entries.

## Read-only project review

`project-review.py --project 01-projects/<note>.md --assert-stop` checks optional
version-bound file-review receipts against canonical task IDs, dependencies and
current input/output bytes. It reports the next eligible authorized work or review;
it never executes tasks or writes notes. Existing task-page UI/status behavior and
manual-task workflows are unchanged. See
[the review protocol](../skills/librarian-controller/references/task-review.md)
for receipt format, explicit sequential fallback and honest completion limits.

## Capture acceptance

`check-capture.py` is an optional, read-only Python 3.9+ helper that works without
Git or local configuration. See `System/skills/capture-acceptance.md` for its
manifest, invocation and explicit semantic limits. It supports the Librarian’s
review; a mechanical PASS alone does not accept a capture or authorize a write.

## Report runners

Three report runners share `run-report.py`:

| Runner | Recipe | Canonical output | Included inactive schedule |
|---|---|---|---|
| `morning-brief.sh` | `System/skills/morning-brief.md` | `03-resources/compound/YYYY-MM-DD-morning-brief.md` | Daily 06:00 |
| `nightly-lint.sh` | `System/prompts/audit.md` | `03-resources/compound/lint/YYYY-MM-DD.md` | Daily 23:30 |
| `weekly-synthesis.sh` | `System/prompts/weekly-synthesis.md` | `03-resources/compound/weekly/YYYY-Www.md` | Sunday 19:00 |

Run from any directory. For example, from the vault root use
`zsh System/scripts/nightly-lint.sh --command /absolute/path/to/assistant-adapter`.
The adapter receives a prompt on stdin and returns only Markdown on stdout.
Configure it to read the vault and use read-only tools; the generic runner cannot
enforce the adapter’s own tool permissions. `PARA_REPORT_COMMAND` can select the
executable instead. It is a single executable path, not a shell command string;
put provider-specific arguments in your adapter. No provider is chosen by default.
For the included optional Claude Code adapter use
`zsh System/scripts/nightly-lint.sh --provider claude`. Add `--dry-run` to inspect the destination without calling Claude, Calendar,
or writing anything. Scripts resolve the vault from their own location.

Requires Python 3 and a configured assistant executable; git improves activity
windows but is optional. The optional Claude adapter requires an authenticated
Claude Code CLI on PATH. A missing/unconfigured command or failed response exits
nonzero and is logged. Generation uses the selected provider’s account/allowance.
No live generation or calendar read is needed to validate installation.

The optional Claude adapter exposes only Read/Glob/Grep tools and no MCP servers.
Other adapters must provide equivalent report-only behavior. The wrapper saves one
new report and appends an activity entry; its own code never edits analyzed notes. The Claude adapter
does not expose file-edit or shell tools; configure equivalent restrictions in
other adapters before use. Treat model findings as findings to review.
Only completed, nonempty responses with required report fields are published.
Per-job advisory locks prevent overlap; existing date/week outputs are skipped,
not overwritten. To revise an existing report, read and update it interactively.
A failed run can be retried after checking the report and runtime log; if the report
was already saved, the retry preserves it. If appending the activity line failed
after publication, add that line manually rather than regenerating the report.
Reports remain uncommitted for review. Commit their explicit paths when reviewed.
New top-level compound listings/index changes are also left for manual review;
the unattended runner deliberately does not modify Home or topic indexes.

Morning brief defaults to vault-only. `zsh System/scripts/morning-brief.sh --provider claude --calendar`
also invokes the optional read-only `read-calendar.py` helper. Choose calendars
through ignored `config.local.json` (`calendar_names`) or pass names explicitly to
the helper. Without configuration it reports unavailable and does not open Calendar.
Configured names are passed as process arguments, not embedded in executable text.
Calendars are queried individually with one retry and bounded timeouts, including
events overlapping today and all-day status. macOS permission may be needed for the
invoking app. Other assistants can use an authorized calendar connector instead;
no particular calendar service is required for the vault.

Runtime logs are `System/logs/<job>.log`; each includes start, success/failure/skip, and
CLI diagnostics. `System/logs/<job>.launchd.log` captures launcher failures if jobs are
later installed. The versioned activity log is `03-resources/vault-log.md`.
Logs grow by appending; archive or rotate old diagnostics as needed. Do not copy another installation's logs into this one.

The inactive examples in `System/scripts/launchd/*.plist.template` contain generic
substitution tokens, not a user's paths or identity. Run
`python3 System/scripts/render-schedules.py` to generate real definitions in ignored
`System/.local/launchd/` for this checkout; optionally set `--vault`, `--output`, or
`--label-prefix`. The default prefix is `org.para-workbench`. Example times can be
edited before rendering. Generation never installs or activates jobs. Configure
the chosen assistant command and verify its job environment before any separately
requested scheduling. Existing installed jobs are not changed by these templates.

## Built-in web clipper

The root `Start PARA Clipper - macOS.command` and
`Start PARA Clipper - Windows.cmd` launchers run the included
`web-clipper` tool. Node.js 22+ is needed for web capture; the existing Python
project/report tools keep their own requirements. The helper defaults to this
vault’s `00-raw` and port 27124. See [the clipper guide](web-clipper/README.md)
for bookmark installation, use, fallbacks, tests, and the capture lifecycle.
