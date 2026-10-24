"""Restricted-token repository audit. No Project scope needed; no GitHub writes."""
from api import *
import re,datetime,collections
m=json.loads((ROOT/'planning/guildboard-backlog.json').read_text());repo=m['repository'];rows=[];page=1
while True:
 r=api(f'repos/{repo}/issues?state=all&per_page=100&page={page}');rows += [x for x in r if 'pull_request' not in x]
 if len(r)<100:break
 page+=1
by={x['id']:x for x in m['items']};actual={};findings=[]
for r in rows:
 marker=re.search(r'<!-- guildboard-id:([^ ]+) -->',r.get('body') or '')
 if not marker:
  findings.append({'issue':r['number'],'kind':'needs_triage','reason':'New issue has no canonical stable ID/metadata; intentionally unassigned is not an error.'});continue
 id=marker[1]
 if id in actual:findings.append({'issue':r['number'],'kind':'duplicate_stable_id','id':id})
 actual[id]=r
 if id not in by:findings.append({'issue':r['number'],'kind':'untracked_id','id':id});continue
 x=by[id];body=r.get('body') or ''
 for section in ['Acceptance Criteria','Review and Verification' if x['work_type']=='Epic' else 'Validation and Evidence']:
  if '## '+section not in body:findings.append({'issue':r['number'],'kind':'missing_section','section':section})
 for label in x['labels']:
  if label not in {l['name'] for l in r['labels']}:findings.append({'issue':r['number'],'kind':'missing_label','label':label})
 if not r['milestone']:findings.append({'issue':r['number'],'kind':'missing_milestone'})
ids=[r['node_id'] for r in actual.values()];native={}
for i in range(0,len(ids),30):
 ns=gql('query($ids:[ID!]!){nodes(ids:$ids){... on Issue{id number state parent{id} blockedBy(first:100){nodes{id state}} subIssues(first:100){nodes{number state}}}}}',ids=ids[i:i+30])['nodes'];native.update({n['id']:n for n in ns if n})
for id,x in by.items():
 if id not in actual:findings.append({'id':id,'kind':'missing_issue'});continue
 r=actual[id];n=native[r['node_id']]
 if x['parent_id']:
  p=actual.get(x['parent_id'])
  if not p or not n['parent'] or n['parent']['id']!=p['node_id']:findings.append({'id':id,'kind':'parent_mismatch'})
 ds={v['id'] for v in n['blockedBy']['nodes']}
 for d in x['dependencies']:
  if d not in actual or actual[d]['node_id'] not in ds:findings.append({'id':id,'kind':'missing_native_dependency','dependency':d})
 if r['state']=='closed' and any(c['state']!='CLOSED' for c in n['subIssues']['nodes']):findings.append({'id':id,'kind':'premature_parent_closure'})
 if '.G' in id and r['state']=='closed' and any(c['state']!='CLOSED' for c in n['blockedBy']['nodes']):findings.append({'id':id,'kind':'premature_release_gate'})
report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Repository labels, milestones, issue bodies, native parents/blockers, enrollment expected by native workflow. Actual Project fields require full audit.py.','issues':len(rows),'findings':findings,'result':'pass' if not findings else 'needs_attention'}
save(ROOT/'planning/audit/repository-integrity.json',report);print(json.dumps(report,indent=2));raise SystemExit(bool(findings))
