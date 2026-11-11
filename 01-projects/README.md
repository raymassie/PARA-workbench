# Projects

A project has a completable finish line; a scheduled end date is optional.
Start as one note from `templates/project-note.md`. Once a second note is needed,
promote it to a folder with a `README.md` from `templates/project-readme.md`.

Every new project includes one actionable checkbox list. Move that list and its
managed progress block into the README during promotion, preserving completed
items and IDs. Double-click `scripts/project-tasks.command` for the task page and
Update button. `prompts/project-update.md` defines updates and follow-through;
`prompts/project-digest.md` refreshes context and status without duplicating tasks.

Completed projects stay in place until a confirmed `prompts/archive-sweep.md`
operation moves them to `04-archive/projects/`.
