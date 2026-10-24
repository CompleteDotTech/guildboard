"""Compile authored capability definitions into stable, fully classified work units."""
from api import *
streams=json.loads((ROOT/'planning/workstreams.json').read_text());state=json.loads(STATE.read_text());ms=list(state['milestones']);items=[]
old={x['id']:x for x in json.loads((ROOT/'planning/guildboard-backlog.json').read_text()).get('items',[])} if (ROOT/'planning/guildboard-backlog.json').exists() else {}
def add(id,title,t,typ,parent=None,requirements='',deps=None,milestone=None,release=None,priority=None,ready=None):
 w=streams[t];dep=deps or [];rel=release or ('MVP' if t in [0,1,2,3,4,5,8] else 'v1.0');pri=priority or ('Critical' if t in [0,1,2,4,5,9,10,12] else 'High')
 meta={'Tier':f'T{t} '+w['name'],'Work Type':typ,'Priority':pri,'Readiness':ready or ('Not Applicable' if typ in ['Epic','Capability','Feature'] else 'Blocked' if dep else 'Ready' if typ in ['Research','Specification','Documentation'] else 'Needs Specification'),'Status':'Backlog','Dependency Status':'Blocked' if dep else 'Unblocked','Release Target':rel,'Risk':'Critical' if t in [1,2,4,5,9,10] else 'High' if typ!='Documentation' else 'Low','Effort':'XL' if typ in ['Epic','Capability'] else 'L' if typ=='Feature' else 'M','Owner Role':w['role'],'Research Confidence':'Unverified','Verification Status':'Unverified'}
 clauses=[x.strip().rstrip('.') for x in requirements.split(';') if x.strip()]
 ac=[c[0].upper()+c[1:]+'.' for c in clauses]
 tests=([f'Provide primary evidence and a reproducible experiment for: {title}; record version, date, limitations and unresolved questions.'] if typ=='Research' else [f'Positive acceptance: {c}.' for c in clauses[:2]]+[f'Negative/failure acceptance: reject unauthorized, malformed, stale and cross-guild inputs for {title.lower()} without side effects.' if t in [1,2,3,4,5,6,8,9] else f'Failure acceptance: exercise invalid configuration, unavailable prerequisites and interrupted execution for {title.lower()}.'])
 labels=['type: '+('workstream' if typ=='Epic' else typ.lower())]+['topic: '+x for x in w['topics']]+['release: '+{'MVP':'mvp','v1.0':'v1.0','Post-v1.0':'post-v1.0'}[rel]]
 x={'id':id,'title':title if typ=='Epic' else id+' — '+title,'workstream':f'T{t}','parent_id':parent,'work_type':typ,'fields':meta,'milestone':ms[milestone if milestone is not None else w['milestone']],'labels':labels,'dependencies':dep,'acceptance_criteria':ac,'expected_tests':tests,'documentation_artifacts':[f'docs/workstreams/T{t}.md'],'requirements':clauses,'assignees':[]}
 for k in ['github','project_item_id','applied_hash','body_hash','comment_id']: 
  if k in old.get(id,{}):x[k]=old[id][k]
 items.append(x);return x
for t,w in enumerate(streams):
 root=f'GB-T{t}';add(root,f'T{t}: '+w['name'],t,'Epic',requirements='Deliver all native child outcomes with accepted evidence; resolve handoffs, security findings and release acceptance; do not close while mandatory descendants remain incomplete')
 add(root+'.R1',w['research'],t,'Research',root,requirements=w['research']+'; record alternatives, primary source URLs, evaluated versions, uncertainty and recommended decision',milestone=0)
 add(root+'.S1',w['contract'],t,'Specification',root,requirements=w['contract']+'; document schemas, invariants, errors, security consequences and test fixtures; obtain consuming engineering review before implementation',deps=[root+'.R1'],milestone=0)
 for c,(cap,features) in enumerate(w['capabilities'],1):
  cid=f'{root}.{c:02}';add(cid,cap,t,'Capability',root,requirements='; '.join(title for title,_ in features)+'; accept implementation, tests and documentation together')
  for f,(title,req) in enumerate(features,1):
   fid=f'{cid}.{f:02}';post=t==13 and c==4 and f==2
   rel='Post-v1.0' if post else None;pri='Low' if post else None
   add(fid,title,t,'Feature',cid,requirements=req,release=rel,priority=pri,milestone=8 if post else None)
   kind='Documentation' if t==13 and c<4 else 'Task'
   deps=[root+'.S1']
   ready=None
   if t==0 and c==3 and f==2:deps=[];ready='Ready'
   impl=add(fid+'.T1',('Document ' if kind=='Documentation' else 'Implement ')+title,t,kind,fid,requirements=req,deps=deps,ready=ready,release=rel,priority=pri,milestone=8 if post else None)
   add(fid+'.V1','Verify '+title,t,'Test',fid,requirements='Execute acceptance scenarios for '+title+'; '+req+'; retain raw results, tested revision/environment and defects; no pass claims from mocks alone for Discord or GoDaddy integration',deps=[impl['id']],release=rel,priority=pri,milestone=8 if post else None)
 add(root+'.D1','Document '+w['name']+' integration and handoff',t,'Documentation',root,requirements='Explain accepted contracts and operator/contributor steps for '+w['name']+'; link actual implementation and test evidence; distinguish planned behavior, supported behavior and unresolved limitations',deps=[root+'.S1'])
# Small independent implementation boundaries with complete contracts.
add('GB-T0.03.02.T1.S1','Implement secret-safe configuration diagnostics',0,'Subtask','GB-T0.03.02.T1',requirements='Return structured CONFIG_INVALID with sorted missing or invalid variable names; never include environment values, database credentials or session secrets; exit nonzero before service binds a listener; snapshot tests contain variable names only',ready='Ready',milestone=1)
add('GB-T0.03.02.T1.S2','Implement strict numeric and URL configuration parsers',0,'Subtask','GB-T0.03.02.T1',requirements='Accept PORT only as base-10 whole integer 1–65535; reject whitespace-only, fractional, exponential, negative and overflow values; accept DATABASE_URL only with mysql protocol and nonempty hostname/database; test all boundary values without logging credentials',ready='Ready',milestone=1)
by={x['id']:x for x in items}
def block(target,*sources):
 x=by[target];x['dependencies']=list(dict.fromkeys(x['dependencies']+list(sources)));x['fields']['Readiness']='Blocked';x['fields']['Dependency Status']='Blocked'
block('GB-T1.03.02.T1','GB-T1.02.01.V1','GB-T1.03.01.V1')
block('GB-T2.01.02.T1','GB-T1.03.02.V1')
block('GB-T4.01.01.T1','GB-T2.01.02.V1','GB-T1.02.02.V1')
block('GB-T4.S1','GB-T3.S1')
block('GB-T4.02.01.T1','GB-T3.01.02.V1','GB-T5.02.01.V1')
block('GB-T5.02.02.T1','GB-T5.02.01.V1')
block('GB-T5.03.01.T1','GB-T5.02.02.V1')
block('GB-T5.03.02.T1','GB-T5.03.01.V1','GB-T5.02.02.V1')
block('GB-T2.02.01.T1','GB-T2.01.02.V1')
block('GB-T2.02.02.T1','GB-T2.02.01.V1')
block('GB-T6.01.02.T1','GB-T2.02.02.V1')
block('GB-T10.02.02.T1','GB-T10.02.01.V1')
block('GB-T10.04.02.T1','GB-T10.02.01.V1','GB-T10.02.02.V1','GB-T10.03.02.V1')
block('GB-T11.03.02.T1','GB-T11.03.01.V1')
block('GB-T12.03.01.T1','GB-T4.02.02.V1','GB-T4.01.02.V1')
block('GB-T12.03.02.T1','GB-T5.03.02.V1','GB-T11.03.02.V1')
block('GB-T9.04.02.T1','GB-T9.01.01.V1','GB-T9.01.02.V1','GB-T9.02.01.V1','GB-T9.02.02.V1')
# Concrete release gates depend on accepted verification, never just merged implementation.
mvp=['GB-T1.01.01.V1','GB-T1.02.01.V1','GB-T1.03.02.V1','GB-T2.01.02.V1','GB-T2.03.01.V1','GB-T3.01.01.V1','GB-T3.04.02.V1','GB-T4.01.01.V1','GB-T4.01.02.V1','GB-T4.02.02.V1','GB-T5.02.02.V1','GB-T12.02.01.V1','GB-T12.03.01.V1']
add('GB-T13.G1','MVP acceptance gate',13,'Test','GB-T13',requirements='Demonstrate Discord startup and authenticated guild context; verify moderator roles and simultaneous moderators; deny viewer writes on backend; demonstrate canvas, live synchronization, saved boards, basic lock and reconnect; attach fundamental security and acceptance evidence',deps=mvp,milestone=2,release='MVP',priority='Critical')
add('GB-T13.G2','Production recovery and GoDaddy acceptance gate',13,'Test','GB-T13',requirements='Demonstrate actual GoDaddy VPS HTTPS/WSS and Discord networking; restore database and assets in isolated environment with measured RPO/RTO; verify monitoring, rollback and production smoke tests; record deployment environment and unresolved findings',deps=['GB-T10.04.02.V1','GB-T11.03.02.V1','GB-T12.04.01.V1','GB-T12.04.02.V1'],milestone=6,priority='Critical')
alltests=[x['id'] for x in items if x['work_type']=='Test' and x['fields']['Release Target']!='Post-v1.0' and not x['id'].endswith(('.G1','.G2'))]
# Gate fan-in stays within supported issue dependency limits by using workstream acceptance gates.
for t in range(13):
 deps=[x['id'] for x in items if x['workstream']==f'T{t}' and x['work_type']=='Test']
 add(f'GB-T{t}.G1',f'T{t} accepted workstream verification gate',t,'Test',f'GB-T{t}',requirements='Confirm all mandatory verification children for '+streams[t]['name']+' have real evidence; resolve defects and security exceptions; verify handoff documentation and integration on release candidate',deps=deps,priority='Critical',milestone=6)
add('GB-T13.G3','Stable v1.0 release approval gate',13,'Test','GB-T13',requirements='All mandatory functionality, modes, moderation, import/export, accessibility and recovery accepted; independent security review findings resolved; production acceptance and full integration tests pass; reviewed versioned artifacts, release notes and support documentation exist',deps=[f'GB-T{t}.G1' for t in range(13)]+['GB-T13.G1','GB-T13.G2','GB-T13.01.01.V1','GB-T13.01.02.V1','GB-T13.02.01.V1','GB-T13.02.02.V1','GB-T13.03.01.V1','GB-T13.03.02.V1'],milestone=7,priority='Critical')
# Handoff documents require the actual verified outcomes they describe.
for t in range(14):
    doc=next(x for x in items if x['id']==f'GB-T{t}.D1')
    doc['dependencies']=list(dict.fromkeys(doc['dependencies']+[x['id'] for x in items if x['workstream']==f'T{t}' and x['id'].endswith('.V1') and x['fields']['Release Target']!='Post-v1.0']))
    gate=next(x for x in items if x['id']==(f'GB-T{t}.G1' if t<13 else 'GB-T13.G3'))
    gate['dependencies'].append(doc['id'])
for x in items:x['description']='; '.join(x['requirements'])
# No guessed issue URLs: rendering resolves only existing GitHub mappings.
save(ROOT/'planning/guildboard-backlog.json',{'schema_version':1,'repository':state['repo'],'project':state['project'],'items':items})
print('Compiled',len(items),'items')
from collections import Counter
print(Counter(x['work_type'] for x in items))
