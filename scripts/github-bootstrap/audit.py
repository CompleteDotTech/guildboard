"""Independent live readback. Does not mutate GitHub. Writes machine-readable findings."""
from api import *
import collections,datetime
m=json.loads((ROOT/'planning/guildboard-backlog.json').read_text());s=json.loads(STATE.read_text());repo=s['repo'];pid=s['project']['id'];findings=[]
def flag(kind,id,detail):findings.append({'kind':kind,'id':id,'detail':detail})
issues=[];page=1
while True:
 rows=api(f'repos/{repo}/issues?state=all&per_page=100&page={page}');issues += [x for x in rows if 'pull_request' not in x]
 if len(rows)<100:break
 page+=1
live={x['number']:x for x in issues};native={}
ids=[x['github']['id'] for x in m['items'] if x.get('github')]
for i in range(0,len(ids),30):
 result=gql('query($ids:[ID!]!){nodes(ids:$ids){... on Issue{id number state parent{id number} subIssues(first:100){totalCount nodes{id number}} blockedBy(first:100){totalCount nodes{id number state}}}}}',ids=ids[i:i+30])['nodes']
 native.update({x['id']:x for x in result if x})
project_items=[];after=None
while True:
 r=gql('query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){nodes{id content{... on Issue{id number repository{nameWithOwner}}} fieldValues(first:30){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}}}}} pageInfo{hasNextPage endCursor}}}}}',id=pid,after=after)['node']['items'];project_items+=r['nodes']
 if not r['pageInfo']['hasNextPage']:break
 after=r['pageInfo']['endCursor']
pitems={x['content']['id']:x for x in project_items if x.get('content') and x['content'].get('id')};required=list(json.loads((ROOT/'planning/project-schema.json').read_text()))
by={x['id']:x for x in m['items']};counts=collections.Counter();field_counts={k:collections.Counter() for k in required};missing=set();edges=[];enrolled=0;native_links=0
for x in m['items']:
 id=x['id'];g=x.get('github')
 if not g or g['number'] not in live:flag('missing_issue',id,'No live issue found');missing.add(id);continue
 r=live[g['number']];n=native.get(g['id']);counts[x['work_type']]+=1
 if not r['assignees']:counts['unassigned']+=1
 b=r.get('body') or ''
 if '## Acceptance Criteria' not in b or ('## Validation and Evidence' not in b and '## Review and Verification' not in b):flag('missing_acceptance',id,'Acceptance or evidence section missing');missing.add(id)
 labels={l['name'] for l in r['labels']}
 for label in x['labels']:
  if label not in labels:flag('missing_label',id,label);missing.add(id)
 if not r['milestone']:flag('missing_milestone',id,'Milestone missing');missing.add(id)
 if x['parent_id']:
  wanted=by[x['parent_id']].get('github',{}).get('id')
  if not n or not n['parent'] or n['parent']['id']!=wanted:flag('parent_mismatch',id,x['parent_id']);missing.add(id)
  else:native_links+=1
 elif n and n['parent']:flag('unexpected_parent',id,n['parent'])
 blockers=n['blockedBy']['nodes'] if n else [];actual={v['id'] for v in blockers}
 for dep in x['dependencies']:
  if by[dep].get('github',{}).get('id') not in actual:flag('missing_dependency',id,dep);missing.add(id)
 for d in blockers:edges.append((g['number'],d['number']))
 item=pitems.get(g['id'])
 if not item:flag('missing_project_item',id,'Not enrolled');missing.add(id);continue
 enrolled+=1;vals={v['field']['name']:v['name'] for v in item['fieldValues']['nodes'] if v}
 for k in required:
  if not vals.get(k):flag('missing_field',id,k);missing.add(id)
  else:field_counts[k][vals[k]]+=1
  if vals.get(k)!=x['fields'][k]:flag('field_drift',id,{'field':k,'planned':x['fields'][k],'live':vals.get(k)})
 openblockers=[d for d in blockers if d['state']!='CLOSED']
 if openblockers and vals.get('Dependency Status')!='Blocked':flag('stale_dependency_status',id,'Open native blocker not reflected');missing.add(id)
 if not openblockers and vals.get('Dependency Status')=='Blocked':flag('stale_dependency_status',id,'No open native blocker');missing.add(id)
 if vals.get('Readiness')=='Ready' and openblockers:flag('false_ready',id,'Unresolved native prerequisite');missing.add(id)
 if vals.get('Status')=='Done' and n and n['subIssues']['totalCount'] and any(live.get(c['number'],{}).get('state')!='closed' for c in n['subIssues']['nodes']):flag('parent_completion',id,'Mandatory open descendants')
 if vals.get('Verification Status')=='Verified' and r['state']!='closed':flag('verification_review',id,'Verified open issue requires evidence review')
for item in project_items:
 content=item.get('content')
 if content and content.get('repository',{}).get('nameWithOwner')!=repo:flag('foreign_project_item',item['id'],content)
graph=collections.defaultdict(list)
for a,b in edges:graph[a].append(b)
seen=set();visiting=set();paths={}
def walk(n):
 if n in visiting:flag('dependency_cycle',str(n),'Cycle detected');return []
 if n in seen:return paths[n]
 visiting.add(n);v=[walk(b) for b in graph[n]];visiting.remove(n);seen.add(n);paths[n]=(max(v,key=len) if v else [])+[n];return paths[n]
for n in list(graph):walk(n)
p=project();schema=json.loads((ROOT/'planning/project-schema.json').read_text());actual_fields={x['name']:x for x in p['fields']['nodes']}
for name,options in schema.items():
 if name not in actual_fields:flag('missing_project_field',name,'Field absent')
 elif [o['name'] for o in actual_fields[name]['options']]!=options:flag('field_option_drift',name,actual_fields[name].get('options'))
expectedviews=json.loads((ROOT/'planning/view-definitions.json').read_text());views={v['name']:v for v in p['views']['nodes']}
for v in expectedviews:
 if v['name'] not in views:flag('missing_view',v['name'],'Absent')
 elif views[v['name']]['layout']!=v['layout'] or views[v['name']]['filter']!=v['filter']:flag('view_drift',v['name'],views[v['name']])
if repo not in [r['nameWithOwner'] for r in p['repositories']['nodes']]:flag('repository_association',repo,'Missing link')
r=api('repos/'+repo);branch=r['default_branch'];branchinfo=api(f'repos/{repo}/branches/{branch}')
for path in ['README.md','LICENSE','SECURITY.md','CONTRIBUTING.md','.github/CODEOWNERS','.github/dependabot.yml','.github/workflows/planning.yml','planning/guildboard-backlog.json']:
 try:api(f'repos/{repo}/contents/{path}?ref={branch}')
 except RuntimeError:flag('missing_repository_file',path,'Not committed on default branch')
settings={}
for name,path in {'actions':'actions/permissions','vulnerability_alerts':'vulnerability-alerts','rules':'rulesets','workflows':'actions/workflows'}.items():
 try:settings[name]=api(f'repos/{repo}/{path}')
 except RuntimeError as e:settings[name]={'unsupported':str(e)}
report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':{'url':r['html_url'],'owner':r['owner']['login'],'visibility':r['visibility'],'default_branch':branch,'license':r.get('license'),'topics':r['topics'],'issues_enabled':r['has_issues'],'head':branchinfo['commit']['sha'],'settings':settings},'project':p,'expected_issues':len(m['items']),'live_expected_issues':sum(counts[k] for k in set(x['work_type'] for x in m['items'])),'project_items':len(project_items),'expected_enrolled':enrolled,'native_parent_links':native_links,'native_blocking_dependencies':len(edges),'counts':dict(counts),'field_counts':{k:dict(v) for k,v in field_counts.items()},'missing_metadata_issues':len(missing),'longest_unweighted_dependency_chain':max(paths.values(),key=len) if paths else [],'findings':findings,'result':'pass' if not findings else 'incomplete'}
save(ROOT/'planning/audit/remote-audit.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['repository','project','findings','field_counts']},indent=2));print('Findings:',len(findings));print(json.dumps(findings[:15],indent=2))
