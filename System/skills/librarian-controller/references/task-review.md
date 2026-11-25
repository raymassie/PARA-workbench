# Version-bound task review

Use this protocol for authorized multi-stage file production. Keep task IDs, wording,
checkboxes and `after:` dependencies in the existing canonical `para-tasks` block.
The adjacent receipts below record authority and evidence, not another task list.
Adopt receipts deliberately for the assignment; existing manual tasks, legacy notes
and external trackers continue through their established Librarian workflow.

## Execute, check, accept, continue

1. Inspect current authority, canonical tasks, pending Librarian flags and existing
   output. Select an authorized task whose prerequisites are accepted. Give its
   worker the actual input version, output paths, permission scope and acceptance
   checks. Resolve scoped failures without overwriting accepted neighboring work.
2. The worker checks actual output and records PASS, REVISE or BLOCKED, with performed
   checks and evidence. A separate checker inspects the actual same version against
   the request and approved standards. The Librarian then confirms the submission,
   inputs, checks and affected project context, recording its own verdict. Native
   independent review uses three distinct actors; PM never replaces this controller.
3. Bind each verdict to the task-definition fingerprint and exact input/output
   manifests. Changed wording, dependencies, inputs or output invalidate affected
   verdicts and descendant readiness. Recheck repaired versions. Preserve accepted
   independent neighbors. A checked box is reported progress; it is not acceptance.
4. After acceptance, continue the next eligible authorized action in the same
   session. Missing review is work to perform, not a reason to stop. A blocked
   branch records its exact reason, evidence and owner/next action; continue other
   eligible work. A paused assignment or actual execution limit must retain remaining
   actions, authority and exact next action. Ending a session never implies a daemon
   continues the work. Global completion still requires the user's explicit finish
   line confirmation; internal acceptance supplies no publication or spending authority.

If native delegation is unavailable, explicitly opt in to `review_mode: sequential`
with `sequential_opt_in: true` for that receipt, perform distinct role passes and
label the result **limited, non-independent**. Retain version binding and the
Librarian's actual confirmation. A task requiring independence sets
`requires_independence: true` and cannot use this fallback. Actor strings are
normalized for comparison, but declarations alone cannot prove separate identities
or that checks ran; the Librarian must inspect evidence.

## Optional read-only helper

Run from the vault root:

```sh
python3 -B System/scripts/project-review.py --project 01-projects/example.md --assert-stop
```

For promoted projects use their canonical `README.md`. The helper derives the graph
from the task page's existing parser, checks local file bytes and routes missing
review/repair/authority without running task text or writing state. It rejects
out-of-vault evidence, self-hashing project notes and nested implementation roots as
canonical lists. Evidence files may be read inside a nested repository; that grants
no write authority there. Exit 1 means eligible work/review remains; malformed or
unsafe metadata exits 2. Without `--assert-stop`, valid routing results exit 0.
`stop_allowed` means no eligible recorded authorized action, **not project success**:
inspect `remaining`, blockers, scope acceptance and finish-line confirmation.
`project_complete` checks accepted current artifact receipts, the recorded explicit
user finish-line confirmation and absence of a pending Librarian flag. It is not
bound to the goal text version and does not prove the goal was met. Before declaring
completion, the Librarian must compare actual output with the current goal and
inspect evidence that the user confirmed that current finish line.

The helper's artifact acceptance covers **file deliverables**. For a human action
such as a call, inspect appropriate source/user evidence in existing project notes;
retain its reported-progress distinction. Do not invent output files to satisfy a
manifest or force optional receipts on every task. A manual or legacy task without
file receipts remains unverified by this helper, not disproven. Existing task-page
status and user finish-line confirmation remain unchanged. Helper JSON is an inline
routing view, never a new saved status file or tracker.

In the SAME canonical note, outside managed task/state blocks, add one optional
`para-review` block with a fenced JSON object. Its fields are:

```json
{
  "schema_version": 1,
  "approval_reference": "Actual user request/date or approved project decision",
  "authorized_tasks": ["implement"],
  "permission_scope": {"implement": ["Edit the approved local implementation paths; no publication"]},
  "tasks": {
    "implement": {
      "definition_sha256": "<fingerprint from helper output>",
      "inputs": {"03-resources/approved-brief.md": "<SHA-256 of current bytes>"},
      "outputs": {"01-projects/example/draft.md": "<SHA-256 of current bytes>"},
      "review_mode": "independent",
      "worker": {
        "actor": "actual worker identity",
        "verdict": "PASS",
        "definition_sha256": "<same fingerprint>",
        "inputs": {"03-resources/approved-brief.md": "<same hash>"},
        "outputs": {"01-projects/example/draft.md": "<same hash>"},
        "checks": ["Specific performed check and result"],
        "evidence": ["Actual file/version and check transcript or observation"]
      }
    }
  }
}
```

Wrap it with `<!-- para-review:start -->` and `<!-- para-review:end -->`.
`checker` and `librarian` have the same binding/check/evidence fields as `worker`,
using their actual actor identities. Librarian PASS also requires
`confirmed_output: true` after inspection. Input manifests may be empty when no
file input exists; PASS requires real output files for artifact acceptance. A worker
blocked before producing output may record an empty output manifest and exact blocker.
BLOCKED reviews add `blocker: {"reason": "...", "next_action": "...", "evidence": ["..."]}`.
Unknown task IDs and incomplete authority are errors. Approval references and scope
are records to verify, never new grants of permission. Keep task/action wording
only in the canonical checkbox list. Receipts support snapshot validation, not a
history of edits that were later reverted or proof of external delivery.

The helper takes no lock because it never writes. Librarian changes still use the
existing shared lock, scoped transaction/checkpoint and recovery journal rules.
Preserve raw/archive sources, pending contextual review and nested-repository
ownership. Report-only runners remain read-only and cannot dispatch writers.
