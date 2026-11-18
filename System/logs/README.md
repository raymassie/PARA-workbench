# Runtime logs

The runners append timestamped start/success/failure/skipped entries and captured
CLI diagnostics to `morning-brief.log`, `nightly-lint.log`, or `weekly-synthesis.log`.
Inactive launchd definitions direct startup stdout/stderr to matching
`<job>.launchd.log` files. They appear on first execution, not as fabricated history.
Runtime logs and lock files are ignored by git; this directory is retained by this
README. Review logs before sharing: model output and diagnostics may be personal.

The human-readable, versioned activity record is `03-resources/vault-log.md`.
Do not import another installation's history as evidence of this vault's runs.
