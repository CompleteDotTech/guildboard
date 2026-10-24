"""Configure the new Guildboard project only. Repeatable schema and taxonomy setup."""
from api import *
s=json.loads(STATE.read_text()); repo=s['repo'];pid=s['project']['id'];p=project();fields={f['name']:f for f in p['fields']['nodes']}
tiers=['Product Foundation & Architecture','Discord Activity & Identity','Authorization & Moderation','Whiteboard Canvas & Editing','Real-Time Collaboration & Presence','Boards, Persistence & Recovery','Collaboration Modes & Presentation','User Interface & Accessibility','Backend APIs & Discord Commands','Security, Privacy & Abuse Prevention','GoDaddy Infrastructure & CI/CD','Reliability, Monitoring & Operations','Quality Engineering & Acceptance','Documentation, Community & Release']
colors=['GRAY','BLUE','PURPLE','GREEN','YELLOW','ORANGE','PINK','RED']
schema={
'Status':['Triage','Backlog','Ready','In Progress','In Review','Blocked','Done'],
'Tier':[f'T{i} {t}' for i,t in enumerate(tiers)],
'Priority':['Critical','High','Medium','Low'],
'Readiness':['Needs Input','Needs Research','Needs Specification','Ready','Blocked','Not Applicable'],
'Work Type':['Epic','Capability','Feature','Task','Subtask','Research','Specification','Test','Documentation','Operations'],
'Research Confidence':['Unverified','Preliminary','Supported','Verified','Disputed'],
'Dependency Status':['Unblocked','Blocked','Awaiting Decision','External Blocker'],
'Verification Status':['Unverified','Tests Pending','Under Verification','Verified','Failed'],
'Release Target':['MVP','v1.0','Post-v1.0'], 'Risk':['Critical','High','Medium','Low'], 'Effort':['XS','S','M','L','XL'],
'Owner Role':['Architecture','Discord Integration','Security & Authorization','Frontend & Canvas','Realtime Systems','Data Engineering','UX & Accessibility','Backend & Bot','Security Engineering','Platform Engineering','SRE','Quality Engineering','Maintainer & Documentation']}
for name,values in schema.items():
 opts=[]
 for i,v in enumerate(values):
  color={'Triage':'GRAY','Backlog':'GRAY','In Progress':'YELLOW','In Review':'PURPLE','Needs Input':'YELLOW','Needs Specification':'ORANGE','Not Applicable':'GRAY','Unblocked':'GREEN','Preliminary':'YELLOW','Supported':'BLUE','Disputed':'RED','Tests Pending':'YELLOW','Under Verification':'BLUE','Critical':'RED','High':'ORANGE','Medium':'YELLOW','Low':'BLUE','Blocked':'RED','Ready':'BLUE','Done':'GREEN','Unverified':'GRAY','Verified':'GREEN','Needs Research':'PURPLE','Failed':'RED','External Blocker':'RED','Awaiting Decision':'YELLOW'}.get(v,colors[i%len(colors)])
  o={'name':v,'color':color,'description':('P'+str(i)+' — '+['release-blocking or foundational','important for v1.0','valuable but nonblocking','optional or exploratory'][i]) if name=='Priority' else v}
  existing=next((x for x in fields.get(name,{}).get('options',[]) if x['name']==v),None)
  if existing:o['id']=existing['id']
  opts.append(o)
 if name in fields:
  gql('mutation($i:UpdateProjectV2FieldInput!){updateProjectV2Field(input:$i){projectV2Field{... on ProjectV2SingleSelectField{id name}}}}',i={'fieldId':fields[name]['id'],'singleSelectOptions':opts})
 else:
  gql('mutation($i:CreateProjectV2FieldInput!){createProjectV2Field(input:$i){projectV2Field{... on ProjectV2SingleSelectField{id name}}}}',i={'projectId':pid,'name':name,'dataType':'SINGLE_SELECT','singleSelectOptions':opts})
 print('field',name,flush=True)
for name,datatype in [('Target Date','DATE'),('Blocking Reason','TEXT')]:
 if name not in fields:gql('mutation($i:CreateProjectV2FieldInput!){createProjectV2Field(input:$i){projectV2Field{... on ProjectV2Field{id}}}}',i={'projectId':pid,'name':name,'dataType':datatype})
r=api('repos/'+repo);s['repository_id']=r['node_id'];save(STATE,s)
gql('mutation($i:LinkProjectV2ToRepositoryInput!){linkProjectV2ToRepository(input:$i){repository{id}}}',i={'projectId':pid,'repositoryId':r['node_id']})
gql('mutation($i:UpdateProjectV2Input!){updateProjectV2(input:$i){projectV2{id}}}',i={'projectId':pid,'public':True,'shortDescription':'Workstream-driven engineering roadmap for Guildboard, a moderated collaborative whiteboard Discord Activity on GoDaddy Linux VPS.','readme':'Guildboard engineering roadmap. Planning is not implementation evidence. Start with Workstream overview, then Ready to implement for actionable leaf tasks. Tier is workstream; Priority is sequencing. No deadlines have been invented. Native dependencies are authoritative for blockers. Assignees remain empty until maintainers take ownership. Manifest, readiness rules, audits and recovery instructions: https://github.com/'+repo+'/tree/main/planning'})
topics='discord discord-activity whiteboard collaboration moderation typescript react excalidraw websockets godaddy self-hosted open-source realtime'.split()
api('repos/'+repo,'PATCH',{'has_issues':True,'has_discussions':True,'allow_squash_merge':True,'allow_merge_commit':False,'allow_rebase_merge':False,'delete_branch_on_merge':True})
api('repos/'+repo+'/topics','PUT',{'names':topics})
api('repos/'+repo+'/actions/permissions','PUT',{'enabled':True,'allowed_actions':'selected'})
api('repos/'+repo+'/actions/permissions/selected-actions','PUT',{'github_owned_allowed':True,'verified_allowed':True,'patterns_allowed':[]})
api('repos/'+repo+'/actions/permissions/workflow','PUT',{'default_workflow_permissions':'read','can_approve_pull_request_reviews':False})
for endpoint in ['vulnerability-alerts','automated-security-fixes']:
 try:api('repos/'+repo+'/'+endpoint,'PUT')
 except RuntimeError as e:print('security setting',endpoint,e)
labels={}
for typ in ['workstream','capability','feature','task','subtask','research','specification','test','security','documentation','operations','bug']:
 labels['type: '+typ]=('5319e7','Work item classification: '+typ)
for t in 'discord-sdk discord-oauth guild-roles authorization canvas excalidraw websockets synchronization concurrency moderation persistence database recovery assets ui accessibility api discord-bot security privacy testing performance godaddy deployment ci-cd observability documentation'.split():labels['topic: '+t]=('0969da','Engineering scope: '+t)
for t in ['mvp','v1.0','post-v1.0']:labels['release: '+t]=('0e8a16','Planned release scope: '+t)
labels['triage: incomplete']=('d73a4a','Automated audit detected missing or inconsistent planning metadata')
existing={x['name']:x for x in api('repos/'+repo+'/labels?per_page=100')}
for name,(color,description) in labels.items():
 if name not in existing:api('repos/'+repo+'/labels','POST',dict(name=name,color=color,description=description))
milestones=['M0 — Research, Feasibility & Architecture','M1 — Repository, Discord & Backend Foundation','M2 — Collaborative Whiteboard MVP','M3 — Moderation, Persistence & Recovery','M4 — Complete Application Functionality','M5 — GoDaddy Production Readiness','M6 — Security, Performance & Final Acceptance','M7 — Stable v1.0 Release','Post-v1.0 — Enhancements and Maintenance']
existing={x['title']:x for x in api('repos/'+repo+'/milestones?state=all&per_page=100')}
for m in milestones:
 if m not in existing:existing[m]=api('repos/'+repo+'/milestones','POST',{'title':m,'description':'Sequence gate; no delivery date committed. Completion requires linked acceptance evidence.'})
s['milestones']={n:v['number'] for n,v in existing.items()};save(STATE,s)
save(ROOT/'planning/project-schema.json',schema);save(ROOT/'planning/audit/configured-project.json',project())
print('Configuration complete',flush=True)

# Public-repository security features; read-back in final audit is authoritative.
api("repos/"+repo+"/private-vulnerability-reporting","PUT")
api("repos/"+repo,"PATCH",{"security_and_analysis":{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"}}})
