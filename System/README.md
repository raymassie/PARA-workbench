# System

The reusable operating setup for PARA-workbench. It uses the same top-level
organization as PARA-brain: prompts, templates, skills, supporting tools, and
runtime logs live under `System/`. Notes stay in the numbered PARA folders.
Root `Librarian.md` remains the canonical policy; root `AGENTS.md`, `README.md`,
and Home remain the entry points.

## Start here

1. Read root `Librarian.md` and `README.md`.
2. Use [Setup](prompts/setup.md) for optional owner preferences, or the
   [workflow catalog](skills/README.md) to choose a capability.
3. Use [Templates](templates/README.md) for the canonical project/task shapes.
   Workbench's project templates retain task, progress, and selected-skill blocks.
4. Open the [Project desk](http://127.0.0.1:8765/) after starting
   `System/scripts/project-tasks.command`, or run
   `python3 System/scripts/project-tasks.py --open`. Its terminal must remain open.
5. Set up only the optional tools you want. The [web clipper](scripts/web-clipper/README.md)
   needs Node.js 22+ and an open terminal. The [Python tools](scripts/README.md)
   need Python 3.9+ and Unix file locking (macOS/Linux). Markdown workflows can be
   used interactively without running those tools.

| Location | Purpose |
|---|---|
| `prompts/` | Filing, project update/review, setup, audit, and weekly workflows |
| `templates/` | Project, area, and topic-index starting shapes |
| `skills/` | Knowledge workflows, project intake, and the specialist/controller library |
| `scripts/` | Project desk, clipper, report runners, calendar reader, tests, and inactive schedule templates |
| `logs/` | Runtime diagnostics and recoverable task journals; private files are ignored |
| `.local/launchd/` | Ignored generated schedule definitions, never automatically installed |

The eight optional specialists, their controller, and guided intake retain their
existing behavior. Skill paths saved by new project intake now point into
`System/skills/`. The task desk still updates the one canonical Markdown task
list, current project state, Home's Projects line, and the activity record.
Reports remain report-only and use the same shared writer lock as task updates.

## Local settings and optional schedules

Owner preferences and the optional calendar allowlist remain in root ignored
`config.local.json`. Report command selection still uses `--command`,
`PARA_REPORT_COMMAND`, or the explicitly selected optional adapter documented in
the tools guide. This folder reorganization does not change account selection,
calendar settings, permissions, or report output locations.

Schedule templates now point at `System/scripts/` and `System/logs/`. Labels,
times, and disabled RunAtLoad behavior are preserved. Rendering writes only
inactive definitions under `System/.local/launchd/`; it does not install, load,
or enable them. Existing installed definitions are not changed by moving source
files. An installed working vault needs a separately authorized update of its
actual job paths and requesting-process permissions.

## Updating an in-use vault

Merge the System paths into local instructions and launchers while preserving
personal settings, working Home sections, content, task IDs, selected-skill
blocks, and independent project repositories. Move local runtime logs and task
recovery journals intact; inspect pending journals before running another writer.
Existing generated definitions should be reviewed and regenerated deliberately,
not silently overwritten. Do not copy empty starter content over working notes.

The old root `prompts/README.md` and `prompts/archive-sweep.md` are thin pointers.
They preserve familiar discovery and the reference in the sealed archive guide;
workflows live only in System. Raw/archive records remain unchanged.

When developing this outbound framework, use temporary vaults for tests. Keep
development trackers, sample tasks/captures, and generated activity out of the
starter content. No automation, background agent, or schedule is activated by
this reorganization.
