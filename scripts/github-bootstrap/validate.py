"""Local structural checks: stable identity, hierarchy, taxonomy and acyclic blockers."""
from api import *
import collections
m=json.loads((ROOT/'planning/guildboard-backlog.json').read_text());items=m['items'];by={x['id']:x for x in items};errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
check(len(by)==len(items),'duplicate stable IDs')
required=['Tier','Work Type','Priority','Readiness','Status','Dependency Status','Release Target','Risk','Effort','Owner Role','Research Confidence','Verification Status']
schema=json.loads((ROOT/'planning/project-schema.json').read_text())
for x in items:
 for k in required:check(x['fields'].get(k) in schema[k],x['id']+': missing/invalid '+k)
 check(x['acceptance_criteria'] and x['expected_tests'],x['id']+': missing acceptance/evidence')
 check(x['milestone'],x['id']+': missing milestone')
 if x['parent_id']:
  check(x['parent_id'] in by,x['id']+': nonexistent parent')
  check(by[x['parent_id']]['workstream']==x['workstream'],x['id']+': unexpected cross-tier parent')
 else:check(x['work_type']=='Epic',x['id']+': orphan')
 for d in x['dependencies']:check(d in by and d!=x['id'],x['id']+': invalid dependency '+d)
 if x['dependencies']:
  check(x['fields']['Dependency Status']=='Blocked',x['id']+': contradictory dependency classification')
  check(x['fields']['Readiness']!='Ready',x['id']+': incorrectly ready with unresolved blockers')
 if x['work_type'] in ['Epic','Capability','Feature']:check(x['fields']['Readiness']!='Ready',x['id']+': broad parent marked ready')
 for label in x['labels']:check(not label.startswith(('priority:','status:')),x['id']+': redundant priority/status label')
children=collections.defaultdict(list)
for x in items:
 if x['parent_id']:children[x['parent_id']].append(x['id'])
for k,v in children.items():check(len(v)<=100,k+': exceeds sub-issue fanout')
def depth(id,seen=None):
 seen=seen or set()
 if id in seen:raise ValueError('hierarchy cycle '+id)
 p=by[id]['parent_id'];return 1 if not p else 1+depth(p,seen|{id})
check(max(depth(x) for x in by)<=8,'hierarchy too deep')
visiting=set();done=set();paths={}
def visit(id):
 if id in visiting:raise ValueError('blocking cycle '+id)
 if id in done:return paths[id]
 visiting.add(id);candidates=[visit(d) for d in by[id]['dependencies']];paths[id]=(max(candidates,key=len) if candidates else [])+[id];visiting.remove(id);done.add(id);return paths[id]
for id in by:visit(id)
check(len([x for x in items if x['work_type']=='Epic'])==14,'expected 14 workstreams')
for t in range(14):check(any(x['workstream']==f'T{t}' and x['work_type']=='Test' for x in items),f'T{t}: missing verification')
report={'result':'fail' if errors else 'pass','item_count':len(items),'native_relationships_expected':sum(bool(x['parent_id']) for x in items),'dependencies_expected':sum(len(x['dependencies']) for x in items),'max_depth':max(depth(x) for x in by),'errors':errors,'longest_prerequisite_chain':max(paths.values(),key=len),'critical_path_note':'Longest unweighted dependency chain, not a duration forecast. Parallel branches and role availability also constrain release.'}
save(ROOT/'planning/audit/local-validation.json',report);print(json.dumps(report,indent=2));raise SystemExit(bool(errors))
