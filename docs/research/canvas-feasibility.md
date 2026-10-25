# GB-T3.R1: pinned canvas research, partial evidence

Issue [#98](https://github.com/CompleteTech-DiscordApps/guildboard/issues/98), observed 2026-10-24 UTC. **Research is incomplete and not accepted.** This record and isolated fixture do not unblock #99, adopt dependencies into the application, or establish editor/server/platform correctness.

## Evaluated version and method

Excalidraw npm `@excalidraw/excalidraw@0.18.1`, source commit `a2ec2889babf7d2295469c6d90ebe77fae57df84`, matches the candidate inspected in PR #477. The source revision and published package are separately identified; source-to-package reproducible build is not proven. Fixture-only React/ReactDOM 18.3.1 satisfy the package's declared peer range. Esbuild 0.25.12 and Playwright 1.56.1 are research tooling, not proposed application tooling.

Read-only primary-source inspection plus a locked local fixture are provided. Node 24.22.1/npm 11.9.0 installed 264 packages with lifecycle scripts disabled. The exact editor tarball integrity is retained in the fixture lockfile and matches PR #477's pin. Neither this install nor a successful bundle establishes full transitive/license/security clearance. Do not distribute this research bundle as the application; #16/#17 retain license and shipped-file review.

## Findings and decision inputs

All source links below point to that immutable revision.

| Scope | Observable source review result | Consequence and unresolved question |
| --- | --- | --- |
| Element identity | [element/types.ts](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/element/types.ts#L39-L79) defines IDs, version, versionNonce, deletion state and customData; [newElement.ts](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/element/newElement.ts#L126-L152) preserves a supplied nonempty ID or generates one. | Preserve server-assigned IDs and tombstones; neither versionNonce nor arbitrary customData proves tenant ownership or accepted revision. The public [convertToExcalidrawElements helper](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/data/transform.ts#L494-L516) regenerates IDs unless `{regenerateIds:false}` is explicitly supplied; the fixture now wraps it with that option. Duplicate IDs, pasted binding remapping and concurrent deletion need adapter tests. |
| Controlled changes / echo | [App.tsx updateScene](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/components/App.tsx#L3885-L3950) replaces scene elements; the [update callback](https://github.com/excalidraw/excalidraw/blob/a2ec2889babf7d2295469c6d90ebe77fae57df84/packages/excalidraw/components/App.tsx#L2875-L2885) invokes onChange outside loading, without a local/remote-origin argument. | Do not interpret every callback as local authorized intent. History capture control is not documented callback suppression. Measure callbacks and use explicit reconciliation/origin bookkeeping, not a guessed timeout, before designing an adapter. Actual echo behavior is unverified here. |
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
npm test
npm run build
node --check probe.mjs
CHROMIUM_PATH=/usr/bin/chromium npm run probe
```

Build uses `--conditions=production`, required by this pinned package's conditional CSS export. The earlier build without the condition failed and was corrected; the final production-condition bundle builds. Output is an unminified research artifact (about 13.1 MiB JS and 160 KiB CSS), **not** a production payload/performance result.

The probe binds only loopback, blocks external page requests, enables Chromium sandboxing, records bounded callback metadata from synthetic elements and closes the browser/server. It never uses production board data or credentials. No screenshots are collected. It is intentionally not added to required CI while the runtime validation remains unavailable.

### Actual result

Install, final bundle build, one non-browser wrapper-contract unit test and JavaScript syntax check passed. The unit test verifies that the wrapper forwards `{regenerateIds:false}` and preserves its input/result references; it does not execute the editor converter or establish rendered behavior. The one attempted browser launch, Chromium 155.0.8059.79, failed **before loading the fixture** with process-singleton `socket() failed: Operation not permitted` and crashpad-directory errors. No sandbox/security options were weakened; launch was not retried through another executor. Consequently **zero browser assertions ran**. The current probe's behavioral assertions are prepared but themselves unvalidated. Do not report them as passing. The full scenario matrix below remains open.

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
