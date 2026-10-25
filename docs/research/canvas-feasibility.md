# GB-T3.R1: pinned canvas research, partial evidence

Issue [#98](https://github.com/CompleteTech-DiscordApps/guildboard/issues/98), initially observed 2026-10-24 UTC and refreshed 2026-10-25 UTC. **Research is incomplete and not accepted.** This record and isolated fixture do not unblock #99, adopt dependencies into the application, or establish editor/server/platform correctness.

## Evaluated version and method

Excalidraw npm `@excalidraw/excalidraw@0.18.1`, source commit `a2ec2889babf7d2295469c6d90ebe77fae57df84`, matches the candidate inspected in PR #477. The source revision and published package are separately identified; source-to-package reproducible build is not proven. Fixture-only React/ReactDOM 18.3.1 satisfy the package's declared peer range. Esbuild 0.25.12 and Playwright 1.56.1 are research tooling, not proposed application tooling.

Read-only primary-source inspection plus a locked local fixture are provided. Node 24.22.1/npm 11.9.0 installed 264 packages with lifecycle scripts disabled. The exact editor tarball integrity is retained in the fixture lockfile and matches PR #477's pin. Neither this install nor a successful bundle establishes full transitive/license/security clearance. Do not distribute this research bundle as the application; #16/#17 retain license and shipped-file review.

### Fixture dependency remediation, 2026-10-25

The original lockfile reproduced 11 affected package entries in `npm audit` (2 high, 7 moderate, 2 low), including transitive propagation. The research fixture now applies the following exact overrides; only these four package entries changed in the lockfile. Excalidraw remains **0.18.1 with the same tarball integrity**, and React, ReactDOM, esbuild, Playwright and other resolved packages are unchanged.

| Consumer / dependency | Publisher declaration / prior resolution | Fixture resolution | Primary evidence |
| --- | --- | --- | --- |
| Excalidraw / Nano ID | `3.3.3` | `3.3.18` | [Maintainer overflow advisory](https://github.com/ai/nanoid/security/advisories/GHSA-xwg4-73v4-xw9w), [3.3.18 release](https://github.com/ai/nanoid/releases/tag/3.3.18) |
| mermaid-to-excalidraw / Nano ID | `4.0.2` | `5.1.16` | [Maintainer 5.1.16 negative-size fix](https://github.com/ai/nanoid/releases/tag/5.1.16) |
| Chevrotain consumers / lodash-es | `4.17.21` | `4.18.1` | Maintainer [template-import injection](https://github.com/lodash/lodash/security/advisories/GHSA-r5fr-rjxr-66jc) and [array-path prototype deletion](https://github.com/lodash/lodash/security/advisories/GHSA-f23m-r3pf-42rh) advisories identify 4.18.1 for lodash-es |
| Mermaid / KaTeX | `^0.16.47` / `0.16.47` | `0.18.2` | [Maintainer inherited-trust advisory](https://github.com/KaTeX/KaTeX/security/advisories/GHSA-238p-pmpm-9mq7) |

These are **fixture runtime overrides, not the dependencies declared by the evaluated publisher tarball**. The Nano ID 4→5 and KaTeX 0.16→0.18 overrides cross the requested ranges. Named Nano ID generation APIs, KaTeX `renderToString`, valid lodash operations, the complete bundle and the bounded browser smoke pass on Node 24.18.0/npm 12.2.0. This does not establish every Mermaid/math/editor workflow's compatibility or authorize application adoption. No force update, editor downgrade, audit suppression or dependency removal was used.

Five new dependency regressions fail against the original lockfile and pass with the overrides: both consumer-resolved Nano ID copies handle zero/negative sizes without hanging; lodash rejects template import expressions and protects prototype properties from array-wrapped paths; KaTeX ignores inherited trust. Generator probes run in owned child processes with a three-second timeout. Together with the existing wrapper test, **6 unit tests pass**. A fresh full `npm audit --json` reports **zero vulnerabilities** on 2026-10-25; that dated registry result is not exhaustive security or license clearance. Exact pins, hashes, counts and historical evidence are retained in the evidence record.

## Findings and decision inputs

All source links below point to that immutable revision.

| Scope | Observable source review result | Consequence and unresolved question |
| --- | --- | --- |
| Element identity | [element/types.ts](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/element/types.ts#L39-L79) defines IDs, version, versionNonce, deletion state and customData; [newElement.ts](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/element/newElement.ts#L126-L152) preserves a supplied nonempty ID or generates one. | Preserve server-assigned IDs and tombstones; neither versionNonce nor arbitrary customData proves tenant ownership or accepted revision. The public [convertToExcalidrawElements helper](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/data/transform.ts#L494-L516) regenerates IDs unless `{regenerateIds:false}` is explicitly supplied; the fixture now wraps it with that option. Duplicate IDs, pasted binding remapping and concurrent deletion need adapter tests. |
| Controlled changes / echo | [App.tsx updateScene](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/components/App.tsx#L3885-L3950) replaces scene elements; the [update callback](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/components/App.tsx#L2875-L2885) invokes onChange outside loading, without a local/remote-origin argument. | Do not interpret every callback as local authorized intent. History capture control is not documented callback suppression. The local smoke observes one callback for one remote hydration; origin classification, echo suppression and proposed-write reconciliation remain unverified. |
| Undo | [store.ts](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/store.ts#L40-L71) distinguishes IMMEDIATELY/NEVER/EVENTUALLY; [updateScene](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/components/App.tsx#L3925-L3934) captures history or updates the snapshot; [history action](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/actions/actionHistory.tsx#L48-L75) operates on local history and excludes view mode. | NEVER is the candidate remote-hydration setting. It does not by itself enforce accepted-intent undo, permission changes, other-user revisions or restore epochs. Server-fenced inverse operations and rollback experiments remain necessary. |
| Assets / serialization | [BinaryFileData](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/types.ts#L91-L105) carries data URLs and file IDs; [JSON serialization](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/data/json.ts#L43-L66) selects local/database output. | Editor serialization is not the trusted server schema. Bound bytes, validate formats, separate private asset authorization and prohibit credential/ephemeral identity persistence. Asset roundtrips, broken images, unsafe imports and export-font embedding remain untested. |
| Accessibility | [Undo ToolButton](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/actions/actionHistory.tsx#L76-L85) has an aria-label and keyboard shortcut. | One accessible control is not an accessibility audit. Keyboard-only editing/navigation, focus after dialogs, screen-reader semantics, contrast and moderated-state announcements need real browser/assistive-technology checks. |
| Touch / stylus | [freehand element type](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/element/types.ts#L354-L370) retains pressures. | Data fields do not establish stylus hardware support or usable gesture behavior. Test pointer capture/cancel, pressure, palm rejection, pinch/pan and Activity clients on actual supported devices. |
| Moderated/read-only editing | [view-mode prop](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/types.ts#L538) and multiple UI guards exist; imperative updateScene does not check the prop. | Read-only is a UX control, never an authorization boundary. A privileged adapter can hydrate a viewer; a forged client must still be denied by the server with zero durable side effects. API mutability in view mode is not itself a defect. |
| Custom editing | Custom data and element composition exist, but the type union is not an arbitrary new-tool plugin contract. | Evaluate bounded text+rectangle grouping for sticky notes, ownership and atomic operations before adopting; do not promise unsupported custom element types. |

## Reproducible local fixture

`research-fixtures/canvas` is deliberately outside root workspaces. It does not change the application manifests. Its lockfile contains third-party research dependencies; generated bundle and node_modules are ignored.

From that directory:

```
npm ci --ignore-scripts --cache /tmp/guildboard-canvas-npm-cache
npm audit --json
npm test
npm run build
node --check probe.mjs
CHROMIUM_PATH=/usr/bin/chromium npm run probe
```

Build uses `--conditions=production`, required by this pinned package's conditional CSS export. The earlier build without the condition failed and was corrected; the final production-condition bundle builds. Output is an unminified research artifact (about 13.1 MiB JS and 160 KiB CSS), **not** a production payload/performance result.

The probe binds only loopback, blocks external page requests, enables Chromium sandboxing, records bounded callback metadata from synthetic elements and closes the browser/server. It never uses production board data or credentials. No screenshots are collected. It is not a required CI gate; portable browser provisioning and the broader runtime matrix remain separate work.

### Actual result

The initial 2026-10-24 attempt using Chromium 155.0.8059.79 failed **before loading the fixture** with process-singleton `socket() failed: Operation not permitted` and crashpad-directory errors. Zero browser assertions ran then; that failure remains in `initial_observation` in the evidence record.

The authorized 2026-10-25 refresh on Windows used Node **24.18.0**, npm **12.2.0**, Playwright **1.56.1** and explicitly supplied cached Chromium **156.0.8078.4** through `CHROMIUM_PATH`. A clean scripts-disabled install, clean full audit, six unit tests, final bundle build, syntax check and planning validation passed. With the overrides installed, the unchanged original `probe.mjs` passed its **three bounded smoke checks**: preserved remote ID, a NEVER-captured remote baseline surviving one local undo, and unchanged content after view-mode pointer/unselected shortcut attempts. It recorded **one remote callback**, **zero blocked external requests** and no page errors. Chromium sandboxing stayed enabled. This browser/version pairing is observed local evidence, not a portable CI or Discord compatibility guarantee.

The wrapper unit test still only verifies forwarding `{regenerateIds:false}` and preserving input/result references. The browser smoke now executes the editor converter, but the full scenario matrix below remains open. In particular, the Delete/undo smoke has no selected element or remaining local history and does not establish those editing controls' protection.

## Runtime matrix still required

1. Remote hydration with NEVER: preserve IDs/tombstones; observe callback counts/origin; prove repeated accepted state does not emit proposed writes.
2. Local edit A then remote edit B then undo/redo: preserve B, express only accepted A inverse, reject stale revisions and prevent forbidden resurrection. Current probe covers only a simpler remote baseline/local-history undo scenario when executable.
3. Reject optimistic local change and rollback; repeat after role revocation/epoch change, reconnect and restore. No accidental re-proposal or polluted undo history.
4. Viewer keyboard shortcuts, pointer drag, delete, paste, drop, text input, context menu and imperative hydration; navigation remains available, server denies every forged mutation. Current probe samples pointer/keyboard UX only. Its Delete/undo attempts have no selected-element/nonempty-history preconditions, so they are merely ineffective-smoke attempts, not proof of those editing controls. Add meaningful preconditions in a separate executable scenario before making that claim.
5. Asset add/roundtrip/export, missing files, excessive data, malformed imports, external URL requests, fonts/CSP and private-file denial.
6. Keyboard-only/assistive technology, touch and real stylus; drag interruption, focus restoration and repeated controls.
7. Compound groups/arrows/text/sticky-note representation; deterministic IDs/bindings, multi-element atomicity and concurrent changes.
8. Actual Discord iframe/proxy/client matrix and agreed large-board latency/memory budgets. Local loopback cannot establish these or GoDaddy deployment behavior.

## Alternatives and recommendation

Continue a controlled adapter experiment, **not adoption**, because public interfaces expose candidate hooks without proving moderated consistency. Maintain an Excalidraw fork only if a documented invariant cannot use public interfaces, with upgrade/security/license cost explicitly accepted. A custom canvas trades control for substantial editing/accessibility maintenance. Full-scene last-write-wins synchronization is not an acceptable fallback for server-authoritative permission and revision requirements.

#98 remains open until missing experiments, functional/security/consumer review, merge and post-merge evidence are resolved. #99 must not treat this partial source review or build as an accepted Tier specification. Discord and GoDaddy provisioning remain out of scope for this fixture.
