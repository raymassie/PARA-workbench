# Vault Audit Prompt

Read the vault and report structural, link, filing, and status problems. Interactive audit is read-only; the explicitly invoked report runner may save its findings.

Run it every month or so, or any time the vault stops feeling trustworthy. Report findings
and propose fixes. **Change nothing without confirmation.**

## Check for

1. **Placeholder leakage.** Any file still containing literal `<date>`, `<topic>`,
   `<project name>`, `YYYY-MM-DD`, or an empty `[[]]`. These mean a template was filled in
   carelessly and shipped. Exclude intentional examples in instructions and templates.
2. **Broken links.** Every `[[wikilink]]` or relative Markdown link whose target does not exist. Also flag
   ambiguous ones where two notes in different folders share a filename, since Obsidian
   resolves by filename and will silently pick one. Ignore example links in code blocks,
   inline code, and comments. Report protected archive issues without editing them.
3. **Unindexed notes.** Notes in `01-projects`, `02-areas`, or `03-resources` that no
   `00-wiki` index points at. These are stored but not findable by topic, which is the
   main way material goes missing in this vault. Propose which index should cover them
   when at least two related notes justify one; a lone note need not have an index.
   Exclude bucket instructions and project-owned implementation files.
4. **Content in the index layer.** Any `00-wiki` note carrying substantive original
   material rather than links and connective prose. That content belongs in
   `03-resources` with the wiki note pointing at it. Propose the move.
5. **Dead indexes.** `00-wiki` notes whose links are missing or whose grouping no
   longer helps retrieval. Links to useful archived records remain valid; an index
   can connect related material across live and archive buckets.
6. **Near-duplicates.** Two or more notes covering the same topic under different names.
   This is the main failure mode as a vault grows: the match search in `translate.md`
   misses an existing note and files a second one. Propose merges of live notes;
   leave sealed archived records intact and link related records instead.
7. **Misfiles.** Notes that fail the Actionability Test where they currently sit. A project
   folder with no end state is really an area. An area with a distinct completable
   finish line may need a project. A date alone does not determine the bucket.
8. **Stale digests.** Project/area summaries that omit or contradict current dated
   notes, decisions, task progress, or uncommitted work. Compare content and dated
   evidence; filesystem modification times after clone/sync are not reliable.
   Propose `prompts/project-digest.md` for the affected project or area.
9. **Stuck captures.** Anything sitting in `00-raw`. Distinguish flagged tasks still waiting
   on the user (expected, by design) from files that failed to process (a problem).
10. **Frontmatter drift.** Inconsistent date formats or key names across notes, which will
   quietly break any Dataview query or sort built on them.
11. **Repository boundaries.** Intentional nested repositories are valid. Check for
   project source tracked by the parent vault repo, vault notes tracked by a project
   repo, missing path-specific implementation exclusions (including archived locations),
   and ambiguous ownership or backup gaps. Ignore rules alone do not prove tracked
   files are excluded. Inspect parent and nested status separately without changing
   either; if Git is unavailable, report the limitation.
12. **Instruction drift.** `AGENTS.md` should be a regular pointer to `Librarian.md`.
   Optional tool-specific pointers must not duplicate or contradict the canonical rules.
13. **Status and action drift.** Check for duplicate live task lists, historical
   checklists presented as current, unlabeled provisional dates or soft targets,
   unsupported completion claims, and READMEs that bury current status in transcripts.

14. **Project state.** Check both single-file projects and promoted folder READMEs:
    explicit active state conflicting with retired/finished content; existing
    `last_session` fields left blank; existing `path` fields pointing at missing
    folders; status contradicting an archived path. Do not add a new mandatory
    project field or replace PARA's existing status format. Use git history rather
    than filesystem timestamps for staleness, including stuck captures older than
    seven days; state when the age is unknown.
15. **Claim consistency.** Check substantive `[CONTRADICTS: ...]` markers against
    `03-resources/contradictions.md`; report missing entries or unresolved links.
    Do not require another vault’s source-page schema or arbitrary outgoing-link counts of
    PARA index notes. Check tags on substantive generated reports where required
    by `skills/README.md`, without imposing a new taxonomy on existing notes.

The unattended `scripts/nightly-lint.sh` runner saves this findings report in
`03-resources/compound/lint/` and appends its activity line. It changes no analyzed
note. Interactive audit remains read-only unless saving a report was requested.
Authorized fixes use `skills/vault-transaction.md`.

16. **Specialist coordination drift.** Librarian.md must remain the controller;
    PM must not introduce a second front door or duplicate task tracker. Check
    roster links, lost source/assumption markers in actual handoffs, misleading
    READY-versus-published claims, conflicting worker write ownership, and role
    outputs filed into indexes or operational skills folders. Do not require
    specialist artifacts for routine filing or force a marketing chain onto
    unrelated research/development work. Report only; no automatic fixes.

17. **Project tasks.** New projects need one canonical actionable task block and
    managed state block. Check missing/duplicate IDs, missing/cyclic dependencies,
    duplicate live lists after promotion, leaked task placeholders, stale progress,
    unresolved pending review flags, and completion claims without finish-line
    confirmation. Preserve historical checklists and designated external trackers.
    Report malformed or unmigrated existing notes; do not silently repair them.

18. **Project intake.** New project records need the goal, explicit start/end
    date answers, date certainty, and a reasoned skill plan (Librarian-only is
    valid). Flag omitted answers, invented dates, end-before-start, leaked intake
    placeholders, lost skills/dates after promotion, unavailable selected skills,
    and suggestions misrepresented as completed agent work. Report only.

19. **Portable setup.** Reusable instructions/configuration should not assume a
    named owner, absolute home-directory path, private calendar list, or another
    personal vault's folders. Keep instance settings in ignored local config;
    preserve license attribution, source records, and protected user content.

20. **Discovery and local preferences.** Home should expose common workflows and
    the full catalog. AGENTS should point to Librarian and the catalog without
    copying rules. CUSTOMIZE should route to guided setup, with personal values in
    ignored local settings. Project reviews must distinguish knowledge gaps from
    structural errors and respect read-only scope.

21. **Archive integrity.** New finished captures should be separate sibling notes
   in the matching archive bucket. Flag evidence of overwrites or edits to sealed
   records, and active work classified as archived solely because history exists.

## Report as

A short list per category, most severe first, with the specific file paths. End with the
three fixes that would most improve the vault's reliability. Do not fix anything yet.
