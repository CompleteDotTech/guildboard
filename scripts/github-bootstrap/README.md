# GitHub bootstrap and reconciliation

Run from this repository using Python 3.11+ and authenticated `gh`. Never put tokens in the manifest or command output. Destination is pinned in `planning/github-state.json`; the reference Project is read-only and no script mutates it.

## Canonical sources

`planning/workstreams.json` contains authored capability requirements. `generate.py` compiles stable work units into `planning/guildboard-backlog.json`, preserving existing remote mappings. Project fields are live execution authority; the manifest records initial planning intent. Do not regenerate during a concurrent reconciliation process.

## Execution

1. `python3 scripts/github-bootstrap/validate.py`
2. `python3 scripts/github-bootstrap/reconcile.py --phase issues`
3. `python3 scripts/github-bootstrap/reconcile.py --phase links`
4. `python3 scripts/github-bootstrap/reconcile.py --phase fields`
5. `python3 scripts/github-bootstrap/reconcile.py --phase comments`
6. `python3 scripts/github-bootstrap/reports.py`
7. `python3 scripts/github-bootstrap/audit.py`

Use `reconcile.py --verify-only` for independent readback. `configure.py` and `views.py` are explicit schema-administration commands; they intentionally reconcile the declared schema/view definitions and should not be run casually after maintainers customize them.

Every issue is detected by durable body marker before creation. Before a failed create is retried, restart the phase to refresh markers, preventing duplication after uncertain transport outcomes. Writes are paced; rate limits back off. Failures log to ignored `planning/audit/failures.jsonl`; review/redact before sharing. Stable mappings persist atomically after every successful creation. Native hierarchy/dependencies are read before repair; a conflicting existing parent aborts instead of replacing legitimate work. Field reconciliation fills missing fields and preserves existing changes after initial triage. Deliberate field drift is reported for review rather than reset. Reruns do not reassign contributors, close issues or repeat marked handoff comments.

## UI-only configuration

GitHub's current public GraphQL view API configures names, layouts, filters and visible fields. Grouping, hierarchy display, roadmap axes, Insights and workflow trigger/action settings are handled in the authorized UI and independently captured in audit artifacts. Inspect the saved settings after changes; URL-only display options are not sufficient proof.

Native auto-add enrolls new Guildboard issues, sub-issue enrollment stays enabled, intake/reopened work returns to Triage, closed work maps to Done, linked PRs map to In Progress and merged PR items map to Done. Automatic issue closure on Project Done is disabled; a status edit is not acceptance evidence. No workflow sets Verification Status to Verified.

## Integrity automation

Repository CI validates manifest identity, metadata, hierarchy limits and dependency cycles. The repository integrity workflow detects missing issue-body criteria, missing milestones/labels, unexpected parent/dependency links and parent closure inconsistency using its restricted repository token. Authenticated `audit.py` additionally checks actual Project field values, enrollment, views, schema and repository association. A scoped `GUILDBOARD_PROJECT_TOKEN` secret can enable that full scheduled audit; the bootstrap does not silently copy a broad personal OAuth token into a public repository's Actions secrets.

New community issues are intentionally untriaged until maintainers supply valid scope and Project metadata. Unassigned work remains visible and is not an error by itself. Review audit JSON findings; never interpret workflow execution alone as application verification.
