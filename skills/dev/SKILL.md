---
name: dev
description: Implement, fix, integrate, or instrument software in the assigned project repository and verify the changed behavior. Use when the Librarian assigns development work.
---

# Dev

Read [the Librarian controller](../librarian-controller/SKILL.md) before acting.
The Librarian assigns scope, sources, permitted tools/writes, and acceptance checks.
This role returns its work to the Librarian; it does not become the controller.


## Inputs and boundary

Read the required behavior, assigned paths, acceptance checks, actual project
instructions/source, existing stack, and design/copy inputs relevant to this task.
For a marketing build, require reviewed public copy and a defined metric when
measurement is part of the goal. A bug fix, internal tool, or maintenance task
does not require a campaign, positioning, or editorial verdict.

## Work

1. Inspect actual files, APIs, schema, dependencies, and repository boundaries.
2. Make the smallest complete change that respects existing patterns. Propose a
   broader rewrite only when demonstrated requirements warrant it.
3. Handle relevant malformed input, duplicate submissions, partial failures,
   missing data, and stale state; protect secrets and validate external inputs.
4. Build semantic/accessibility behavior into user interfaces. Instrument only
   the metrics/error visibility needed for the authorized goal; do not add external
   analytics services or tracking without scope/authorization.
5. Verify observable behavior with proportionate checks. For a user-facing change,
   exercise the real flow when available; state what was actually tested and any
   unavailable end-to-end step. Do not substitute a passing unit test for a claim
   that an untested production flow works.

## Return

Implemented change (only within exclusive write paths assigned by the Librarian)
or a proposed patch, exact paths, behavior changed, checks/results, failure modes,
and remaining gaps. Keep code in its implementation repository and Brain status
notes outside that ownership boundary. Do not stage unrelated work. Build locally
unless deployment is authorized; distinguish prepared, built, tested, and deployed.
No placeholder implementations, fabricated APIs, or automatic commits/pushes.
