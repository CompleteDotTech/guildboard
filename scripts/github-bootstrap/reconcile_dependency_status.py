"""Reconcile derived native blocker state without declaring any issue Ready/Done.
Preserves explicit external/decision classifications and all contributor assignments.
"""
from api import *
import concurrent.futures
s=json.loads(STATE.read_text());base='users/'+s['owner']+'/projectsV2/'+str(s['project']['number']);fs={f['name']:f for f in api(base+'/fields?per_page=100')};pid=s['project']['id'];after=None;changes=[]
def option(name,value):return next(o['id'] for o in fs[name]['options'] if (o['name']['raw'] if isinstance(o['name'],dict) else o['name'])==value)
while True:
 r=gql('query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){nodes{id fullDatabaseId content{... on Issue{number blockedBy(first:100){nodes{state}}}} fieldValues(first:30){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}}}}} pageInfo{hasNextPage endCursor}}}}}',id=pid,after=after)['node']['items']
 for item in r['nodes']:
  if not item.get('content'):continue
  vals={v['field']['name']:v['name'] for v in item['fieldValues']['nodes'] if v};open_blockers=any(b['state']!='CLOSED' for b in item['content']['blockedBy']['nodes']);cur=vals.get('Dependency Status');updates=[]
  if open_blockers and cur in [None,'Unblocked']:updates.append({'id':fs['Dependency Status']['id'],'value':option('Dependency Status','Blocked')})
  elif not open_blockers and cur=='Blocked':
   updates.append({'id':fs['Dependency Status']['id'],'value':option('Dependency Status','Unblocked')})
   if vals.get('Readiness')=='Blocked':updates.append({'id':fs['Readiness']['id'],'value':option('Readiness','Needs Input')})
  if updates:changes.append({'id':item['fullDatabaseId'],'issue':item['content']['number'],'updates':updates})
 if not r['pageInfo']['hasNextPage']:break
 after=r['pageInfo']['endCursor']
def apply(x):api(base+'/items/'+str(x['id']),'PATCH',{'fields':x['updates']});return x['issue']
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for issue in pool.map(apply,changes):print('Reconciled native dependency state',issue,flush=True)
save(ROOT/'planning/audit/dependency-status-repair.json',{'changed':changes,'policy':'Native open blockers prevent Unblocked; satisfied native prerequisites require readiness review, never automatic Ready/Done. External/decision states are preserved.'});print('Changed',len(changes),flush=True)
