# Guildboard engineering and review instructions

These instructions apply throughout this repository. Follow `CONTRIBUTING.md`,
`GOVERNANCE.md`, `SECURITY.md`, the live issue and Project, and accepted contracts.
This file adds implementation and review checks; it does not waive their gates,
appoint reviewers, authorize agent delegation, or change issue readiness.

## Scope, ownership and architecture

- Use the canonical repository, `CompleteTech-DiscordApps/guildboard`. Inspect the
  live issue, stable GB ID, native blockers and open PRs before claiming work.
  Coordinate ownership with the maintainer and existing owner; preserve unrelated
  work and use a focused branch or isolated worktree. Do not create duplicate work.
- Read `docs/architecture.md`, the applicable `docs/workstreams/T*.md` and accepted
  ADRs. The scaffold and proposed contracts do not establish a working product.
  Do not implement unresolved runtime architecture across native research or
  specification blockers. The bounded configuration contract in
  `planning/configuration-contract.md` is an explicitly documented exception.
- Preserve the Activity/API/bot, shared contract, canvas adapter, collaboration,
  database and infrastructure boundaries. Version protocol/schema changes and
  document consumer compatibility, ownership and handoffs. Significant design
  changes require an ADR with alternatives, failure behavior and security effects.
  Avoid independently invented, incompatible synchronization or policy systems.

## Security and authorization review

- Treat client user, guild, channel, role, permission and administrator claims as
  untrusted. Verify Discord OAuth exchanges, least-privilege scopes, launch and
  interaction provenance, redirect/origin constraints, session binding, expiry,
  renewal and replay/CSRF defenses against the accepted identity contract. Keep
  bot tokens, OAuth credentials, sessions and board content out of logs and URLs
  where they could leak; use the private reporting route in `SECURITY.md`.
- Enforce deny-by-default policy on the backend for every read, mutation, command,
  upload, export and socket operation. UI read-only state is only feedback.
  Check current membership, role mapping, board visibility, mode, restrictions,
  object ownership and grant expiry as applicable. Prevent self-escalation,
  self-approval and moderator escalation. A socket handshake is not continuing
  authorization: role removal, revocation and emergency lockdown must fence
  in-flight writes and already-connected clients using the accepted policy
  generation/ordering contract. Use server time for grant expiry.
- Scope database queries, joins, caches, room names, operation/idempotency IDs,
  asset references, audit access and broadcasts by verified tenant and board.
  Attempt forged and guessed IDs, cross-guild and cross-board access, stale roles,
  expired grants and replay. Denials must have no unauthorized durable or broadcast
  side effects and must not leak another tenant's existence or content.
- Authorize request-to-draw, grant/revoke, lock/unlock and restriction transitions;
  record scoped actor, action, policy generation and outcome with audit integrity
  and appropriate retention. Lockdown must override ordinary writer grants.
- Validate imports/uploads by content as well as declared type; bound file size,
  decoded dimensions, element count and parser work. Prevent active-content/XSS,
  SQL injection, path traversal, unsafe filenames and unsafe remote fetch/SSRF.
  Keep assets private and scoped; authorize retrieval and deletion. Bound HTTP/WS
  payloads, rates, queues, connections, timers and storage per user/board/guild.
  Test resource exhaustion, slow consumers and cleanup without dropping accepted
  durable operations or affecting other tenants.

## Collaboration, persistence and recovery review

- Authenticate and scope WSS upgrades, room joins and reconnects; enforce accepted
  origin/proxy rules and versioned operation schemas. Server-sequence accepted
  intent with monotonic per-board revisions, scoped idempotency and explicit base
  revisions. Preserve canonical element identity, deterministic same-object
  conflicts, compound atomicity and revision-aware undo. Do not use naive
  full-document last-write-wins as a concurrency shortcut.
- Commit the operation, resulting durable state and receipt atomically before
  acknowledging acceptance. Test concurrent duplicate IDs, retry after lost ACK,
  rollback, process crash and restart; do not equate delivery exactly once with
  logical idempotency. Separate bounded, lossy ephemeral presence from durable
  edits and avoid exposing hidden participants.
- Test simultaneous edits, deletion/groups, mode and presenter changes, grant
  revocation races, delayed/duplicate/reordered frames, disconnect/reconnect,
  late join and slow clients. Compare canonical board hashes and revision history
  after quiescence. Snapshots need a consistent cut, bounded snapshot-plus-tail
  replay, lineage and retention rules; stale epochs must not resurrect content.
- Review MySQL/MariaDB tenant constraints, indexes, transactions and locking under
  concurrency. Migrations need version compatibility, interruption/retry behavior,
  data preservation and a documented rollback or forward recovery path. Prove
  backup plus assets/logs can restore into an isolated environment; measure achieved
  RPO/RTO. A backup file or a model-only test does not prove recoverability.

## Configuration, deployment and user experience

- Apply `planning/configuration-contract.md` exactly; invalid configuration must
  produce names-only diagnostics without secret values or side effects in pure
  parsing. Successful configuration contains credentials and must not be logged.
  Runtime entry points fail before binding on invalid config. Keep environment
  secrets separate, ignored and outside source/images; review rotation and access.
- Production targets a GoDaddy Linux VPS with Nginx HTTPS/WSS, private database
  and persistent assets. Review TLS renewal, Discord Activity proxy mappings,
  DNS/origins, WebSocket timeouts, least-privilege services, health checks, graceful
  shutdown, migration ordering, secret handling and rollback. Do not silently
  replace mandatory hosting or infer real Discord/VPS behavior from local mocks.
- For Activity/UI changes verify keyboard and focus behavior, labels and screen
  reader feedback, contrast, touch, reduced motion and responsive Discord
  viewports. Cover permission/request outcomes, loading, save state, reconnect and
  errors. Canvas interactions need practical accessible alternatives; automated
  accessibility scores alone are not acceptance.

## Validation and mandatory review gates

- Run `python3 scripts/github-bootstrap/validate.py` for planning changes and
  applicable focused behavior, integration, security and regression checks for
  implementation. Use the commands present on the current branch; do not invent
  a working app/build. Add meaningful allow/deny and no-side-effect tests for each
  changed authorization boundary, plus relevant concurrency and failure cases.
- Record exact commands, environment, tested full commit SHA, results and limits.
  Distinguish model/fixture tests, local integration, hosted CI, real Discord
  clients, real GoDaddy verification and post-merge acceptance. Research, a green
  planning check, a review request or merged documentation proves none of the
  untested runtime claims. Mark unavailable checks as pending or blocked.
- Before merge, obtain actual Copilot review and a fresh independent
  `gpt-6.1-sol` review at **MAX reasoning** against the actual current PR head SHA,
  covering the delta and relevant integration. Record reviewer identity/tool,
  configuration, reviewed SHA, findings and disposition with links. A request,
  assignment, author self-review, stale review or fabricated clean report is not
  completed review. These requirements do not provision paid agents or authorize
  delegation; if a reviewer is unavailable, keep the gate pending and report it.
- Resolve actionable findings, then obtain both reviews again on the new head
  after any change. Read back the live PR head, review evidence and current checks
  before merge. Required functional/security expertise, CODEOWNER approvals,
  native prerequisite gates and passing required CI remain separate requirements.
  Never bypass branch protection, use an administrator override, weaken tests or
  relabel blockers to manufacture readiness. Merge only with explicit authority.
- Link the relevant issue without closing directives until its full Definition
  of Done is satisfied. Do not close parent issues with incomplete mandatory
  descendants or claim a production release/deployment without dated evidence.
