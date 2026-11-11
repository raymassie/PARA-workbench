# Templates

Starting shapes for the files agents create in this vault. You will rarely open this folder yourself. `prompts/translate.md` and `prompts/project-digest.md` read from it when they need to create something new.

| Template | Used when creating | Lands in |
|---|---|---|
| `project-note.md` | a project's first note | `01-projects/<name>.md` |
| `project-readme.md` | a project's status file, once it's promoted | `01-projects/<project>/README.md` |
| `area-note.md` | an area's first note | `02-areas/<name>.md` |
| `area-readme.md` | an area's status file, once it's promoted | `02-areas/<area>/README.md` |
| `wiki-note.md` | a new topic index (Map of Content) | `00-wiki/<topic>.md` |

Projects and areas start as a single file and only get promoted to a folder with a
`README.md` once a second note joins the first. `prompts/project-digest.md` and
`prompts/translate.md` both know how to do that promotion.

Notes in `03-resources` have no template, and resource folders don't get a `README.md` either. That job belongs to the `00-wiki` topic index for the subject; a second table of contents at the folder level just duplicates it.

Before filling a project template, run `skills/project-intake/SKILL.md`. Gather the
goal, start/end dates (or explicit undecided), and end-date type; choose project
skills with a reason and invocation stage. Both templates preserve those values
and the marked skill plan through promotion. Never default an unanswered date.

Both project templates include a canonical task block and a separate managed
progress block for the Project desk Update button (`scripts/project-tasks.command`).
Fill each task with a concrete action and observable completion check; preserve
stable task IDs and never ship the example placeholder. See
`prompts/project-update.md`. During promotion, move the current blocks to the
README rather than leaving two live lists. Preserve all user fields such as Due.

Every placeholder in these files (`<project name>`, `YYYY-MM-DD`, and so on) must be replaced with a real value before a filed note is saved. See Rule 8 in `Librarian.md`. Unknown facts should be labeled unknown rather than invented; template and instruction examples may retain placeholders.
