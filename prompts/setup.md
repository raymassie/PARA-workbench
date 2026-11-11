# Guided owner setup

Use when the user asks to customize the vault, or offer once at first use if the
local owner profile is missing/incomplete. The Librarian conducts this conversation;
no extra agent or setup service is needed. Keep the user's current work moving.

Read `config.example.json` and optional ignored `config.local.json`. Reuse answers
already supplied for this setup; do not infer preferences from filenames, clipped
articles, a home-directory name, or a source vault. Explain that these answers stay
local and the reusable Librarian guide stays generic.

Ask a compact set of questions, no more than three at once:
1. What should I call you, and what work or responsibilities should this vault support?
2. What subjects recur, and how should your notes read?
3. What wording, formatting, or behavior should I avoid?

Allow the user to skip optional identity/context or keep the shared writing defaults.
Clarify only an answer that materially changes behavior. Show the interpreted
preferences briefly and save the supplied/accepted values to `owner` in
`config.local.json`, preserving unrelated keys and calendar settings. Set
`owner.setup_complete` true after answered or explicitly skipped/defaulted fields;
do not repeatedly ask on every session. If saving is unavailable, state that it
was not persisted and provide the completed preferences for the user.

The CUSTOMIZE section in `Librarian.md` describes these local fields; never replace
the shared policy with one person's profile. Do not put identity or private calendar
names into templates, committed documentation, Home, or logs. The user can reopen
setup to revise preferences at any time. A read-only request does not authorize a
profile write; setup answers provided for saving do.

Finish by pointing to Home's “Ask the Librarian” menu and `skills/README.md`.
Explain available workflows and any optional setup they require; selecting a
workflow does not mean it ran or grant calendar/account permissions.
