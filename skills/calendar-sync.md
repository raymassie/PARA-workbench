# Calendar sync

Trigger: “Sync my calendar”, “Plan today”, or “Calendar sync”.
Read `skills/README.md` first. Use the calendar source the user has configured;
do not assume a provider, account, calendar name, or destination for new events.

1. Read today's schedule from an available authorized connector. On macOS, the
   optional `python3 scripts/read-calendar.py` helper reads only calendar names in
   ignored `config.local.json`, or explicit `--calendars` arguments. Empty/missing
   configuration means unavailable, not an empty schedule; do not enumerate private
   calendars or guess the user's choices. Query configured calendars individually
   and retry a failed read once to isolate calendar-specific failures.
2. Include overlapping and all-day events; sort timed events separately. Report
   inaccessible calendars distinctly from successfully read empty ones. macOS may
   require Calendar permission for the invoking app. Do not bypass denied access.
3. Compare current dated intentions and active project/area notes. Cite specific
   notes/events for unprepared events, unscheduled priorities, and conflicts.
4. Offer slots where useful. Creating/changing events requires authorization and
   a specified destination calendar. Check an uncertain write outcome before retrying.

Save `03-resources/compound/YYYY-MM-DD-calendar-sync.md` when vault writes are in
scope, using Today's schedule, Unprepped, Unscheduled, and Conflicts sections.
Otherwise return inline. Follow shared logging/indexing rules. The helper is
read-only; installing the workflow grants no permissions and performs no query.
