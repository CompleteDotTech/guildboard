# Execution notes and limitations

The reference was read before creation and used only as a read-only template. The destination owner was resolved from the active authenticated account, CompleteDotTech. Project #7 was copied with draft copying disabled; independent initial readback found zero copied items. Repository association and Guildboard-only auto-add were created separately.

## Verified UI configuration

- Overview: first saved view, table, Tier grouping, hierarchy On, required columns plus Verification Status and Release Target.
- Engineering backlog: Priority grouping (Critical first by option order), hierarchy Off.
- Workload: actual Assignees grouping with count; no contributors invented.
- Kanban: inherited native Status columns; cards expose priority, assignee, Work Type and dependency state.
- Roadmap: monthly timeline grouped by milestone; Target Date configured as target axis, all dates blank.
- Insights: default Burn up copied with `is:issue`; source and target had no custom charts.
- Auto-add: Guildboard repository, issues only (UI normalizes the rule to `is:issue,pr is:issue`). New items and reopened items→Triage. Native sub-issue enrollment enabled. Closed items→Done. Linked PR→In Progress; merged PR items→Done. Auto-close issue on Project Done disabled. No rule sets verification or research confidence to Verified.

Project API supports view layouts/filters/visible fields, but grouping/hierarchy/dates/workflow actions were configured in authorized UI. Final audit reads native groupings and columns independently; UI-only details are recorded here and in the final screenshot.

## Repository safeguards

MIT applies to original source; dependency/asset compatibility review remains an explicit issue. Main rules block deletion/non-fast-forward updates and require one approving CODEOWNER review, resolved threads and the observed successful `Validate roadmap` GitHub Actions check. Repository administrators have an explicit bootstrap bypass. No review was fabricated for the bootstrap commits.

Actions, Issues, Discussions, Dependabot alerts/security updates, secret scanning, push protection and private vulnerability reporting are enabled. Application CodeQL/runtime test coverage is future work because runtime source is not implemented. Security scanning configuration is not an independent product security review.

## Automation credential boundary

Daily restricted-token repository integrity checks and local manifest CI are configured. Full live Project metadata auditing is repeatable through authenticated `audit.py`. Scheduled full Project field auditing additionally requires a dedicated supported read-Project credential in `GUILDBOARD_PROJECT_TOKEN`; no broad personal OAuth token was copied into Actions. Native Project automation does not need that secret. User-owned Project REST endpoints currently do not accept installation/fine-grained tokens.

## Rate limiting and recovery

GitHub began rejecting new issue content at 2026-10-24T02:52 UTC after 428 roadmap issues. Creation retries were stopped; native links, field triage and read-only verification continued. The manifest records only successful issue responses. Resume creation after the service's cooldown and refresh stable markers before retrying; never switch accounts/APIs to evade a service limit. Final remote audit, not this note or an operational checkpoint, determines completion and counts.

Transient GraphQL relationship errors were retried only after fresh live reads. Earlier failures are not evidence of unresolved defects when the final native readback confirms repair.
