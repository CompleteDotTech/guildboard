# Guildboard mandatory review guidance

Apply `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, accepted ADRs and the live
issue's scope, GB ID and native blockers. Inspect integration. Give located,
reproducible findings with impact; distinguish evidence from assumptions.
Do not invent defects or unperformed checks. Explain non-applicable areas.

Review affected boundaries:

- Discord OAuth, sessions and roles: verify code exchange, least-privilege scopes,
  origin/redirect and replay/CSRF defenses, expiry and verified guild/channel
  provenance. Never trust client roles/admin flags or expose tokens/secrets.
- Backend authority: deny by default on reads, writes, commands, exports, assets
  and WebSocket messages. Check current membership, role, mode, object policy,
  restrictions and grants. UI read-only state and a handshake are insufficient.
  Revocation/role removal/lockdown must fence active sockets and in-flight writes;
  grant TTL uses server time. Test allow/deny, stale/replayed claims and no side
  effects. Prevent self-approval, privilege escalation and unsafe moderation.
- Multi-guild isolation: tenant/board-scope every query/join, cache, room, broadcast,
  operation ID, asset and audit lookup. Test cross-guild/board/object access,
  leakage and concurrent users.
- Collaboration: versioned bounded messages, authenticated WSS, server sequencing,
  monotonic board revisions, scoped idempotency, explicit base revisions,
  deterministic element conflicts, compound atomicity and revision-aware undo.
  Reject naive full-document last-write-wins. Test duplicate/reordered/dropped
  frames, simultaneous edits, mode/presenter/revocation races and reconnect;
  compare canonical hashes and durable history for convergence.
- Persistence: atomically commit operation/state/receipt before ACK; test lost
  ACK retries, concurrent duplicates, crash/restart and transaction rollback.
  Review tenant constraints, MySQL/MariaDB locking, consistent snapshot cuts,
  lineage and bounded replay. Migrations need compatibility and interruption/
  recovery checks. Backup acceptance requires isolated restore with assets/logs
  and measured RPO/RTO.
- Abuse/privacy: validate upload/import content, bytes, dimensions and element
  counts; prevent XSS, SQL injection, path traversal and SSRF. Authorize private
  assets and moderation/audit access. Bound rates, queues, connections, storage
  and work; test slow consumers/exhaustion and cleanup. Keep presence ephemeral.
- Config/platform: follow `planning/configuration-contract.md`; no secrets in
  diagnostics or successful-config logs. Verify fail-before-bind startup. Target
  GoDaddy Linux VPS, Nginx HTTPS/WSS, private DB and persistent assets; inspect
  Discord proxy/DNS/origins, TLS renewal, health, shutdown and rollback.
- UI/architecture: keyboard/focus, screen readers, contrast, touch, reduced motion,
  responsive Discord views, save/error/permission feedback and canvas alternatives.
  Preserve accepted service/adapter contracts; significant changes need an ADR.

Require meaningful negative, failure, concurrency and regression tests.
Planning changes run `python3 scripts/github-bootstrap/validate.py`.
Record commands, environment, exact SHA, results and limits. Local/model/mock
checks do not prove real Discord, GoDaddy, recovery or production acceptance.

Before merge require actual Copilot review AND fresh independent `gpt-6.1-sol`
**MAX reasoning** review of the current full PR head SHA and relevant integration;
record linked evidence and resolve findings. Re-review both after any head change.
A request, self-review or stale result is insufficient. Preserve required CI,
CODEOWNER/security review and native gates; never bypass protections or weaken
tests. Unavailable review stays pending. This file grants no delegation authority.
Reference issues without closing directives until their full Definition of Done;
never claim deployment or completed capabilities from scaffolds or documents.
