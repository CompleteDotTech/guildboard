# Reference inspection

Reference: https://github.com/orgs/Pick-Your-AI/projects/1 . Read-only API snapshot is `reference-project.json`. UI inspection additionally checked every saved view and Insights. No source Project mutation was performed.

Title: **Pick Your AI — Research — AI Builder**. Description: research for a PCPartPicker-inspired AI system builder spanning configuration, models, infrastructure, retrieval, agents, training and operations.

Eight saved views: Workstream overview, Research backlog by priority, Ready to research, Blocked or awaiting decision, Unassigned or missing metadata, Kanban, Owner Workload, Roadmap. Exact filters, field types, option IDs/colors/descriptions and visible field ordering are preserved in the raw snapshot.

Overview is a dense table showing Title, Assignees, Status, Tier, Priority, Readiness, Parent issue, Sub-issues progress, Labels, Work Type, Research Confidence and Dependency Status. UI shows native expandable workstream rows and child completion fractions. Saved grouping is none, sorting manual, hierarchy On. Backlog/ready/blocked/metadata tables likewise have no grouping and manual sorting, with hierarchy On. Backlog includes Labels; Ready omits Labels. Parent issue is visible in those focused tables.

Kanban is a board with Status columns, no swimlanes, manual sorting, count aggregation; visible fields include Title, Assignees, Status, Linked pull requests and Sub-issues progress. Owner Workload is a table with those same fields, no saved grouping, manual sorting and hierarchy On. Roadmap uses monthly zoom, no dates, markers or saved grouping, manual sorting. Insights has only default Burn up and no custom charts; its filter is `is:issue`.

Six enabled source workflows: auto-add sub-issues, auto-close issue, item added, item closed, PR linked to issue and PR merged. The copied rules were inspected in the new Project: added→Backlog, closed→Done, linked PR→In Progress, merged PR→Done and Project Done→issue close. Guildboard adapts intake/reopen to Triage and disables automatic issue closure. A separate Guildboard-only auto-add rule was created because source integrations are excluded from copying.

Source taxonomy uses descriptive `type:` and `topic:` labels. Source Work Type options are Epic, Research, Specification, Dataset and Validation. Native issue types were null in sampled issues. Tier is T0–T6 workstream, separate from Critical/High/Medium/Low priority. Confidence is Unverified/Low/Medium/High; dependency status Unblocked/Waiting/Blocked. Assignees are actual source contributors, often multiple; none were copied to Guildboard.

Parent writing emphasizes product question, scope, native children, handoff boundaries, acceptance and actual owner. Focused children specify question, scope, source/evidence fields, deliverable, dependency table and acceptance conditions. Native blockers impose real sequencing; informational and compatibility inputs do not. Evidence grading and research completion are explicitly separate from implemented product behavior. The metadata view surfaces unassigned/missing priority, Tier and readiness. Guildboard preserves those disciplines while adding engineering verification, release, risk, effort and functional owner fields.

The source has some completed research/PR rows with empty metadata and Unverified confidence. Those historical states were not imported or treated as Guildboard evidence. Guildboard's grouping and workload organization deliberately improve the current saved configuration to satisfy the user's explicit Tier/assignee grouping requirements.
