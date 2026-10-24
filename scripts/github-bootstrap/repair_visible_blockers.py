"""Derive visible blocker links from the live native graph. No execution state edits."""
from api import *
import concurrent.futures,re
s=json.loads(STATE.read_text());pid=s['project']['id'];base='users/'+s['owner']+'/projectsV2/'+str(s['project']['number']);field=next(f for f in api(base+'/fields?per_page=100') if f['name']=='Blocking Reason');pending=[];after=None;checked=0;manual_conflicts=[]
while True:
 r=gql('query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){nodes{id fullDatabaseId content{... on Issue{number blockedBy(first:100){nodes{url state}}}} fieldValues(first:30){nodes{... on ProjectV2ItemFieldTextValue{text field{... on ProjectV2Field{name}}}}}} pageInfo{hasNextPage endCursor}}}}}',id=pid,after=after)['node']['items']
 for item in r['nodes']:
  if not item.get('content'):continue
  checked+=1;urls=sorted(b['url'] for b in item['content']['blockedBy']['nodes'] if b['state']!='CLOSED');old=next((v['text'] for v in item['fieldValues']['nodes'] if v and v['field']['name']=='Blocking Reason'),'')
  current=set(re.findall(r'https://github.com/[^\s,]+',old));expected=blocker_summary(urls)
  if old and not old.startswith(('Await accepted prerequisites:','Await ')):
   if set(urls)!=current:manual_conflicts.append(item['content']['number'])
   continue
  if urls and old!=expected:pending.append((item['fullDatabaseId'],expected))
  elif not urls and old.startswith(('Await accepted prerequisites:','Await ')):pending.append((item['fullDatabaseId'],None))
 if not r['pageInfo']['hasNextPage']:break
 after=r['pageInfo']['endCursor']
def repair(row):
 id,text=row;api(base+'/items/'+str(id),'PATCH',{'fields':[{'id':field['id'],'value':text}]});return id
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for id in pool.map(repair,pending):print('Reconciled visible native blockers',id,flush=True)
save(ROOT/'planning/audit/visible-blockers.json',{'checked':checked,'repaired':len(pending),'preserved_manual_conflicts':manual_conflicts,'source':'Live native blockedBy relationships; no status/readiness/assignee overwritten.'});print('Checked',checked,'repaired',len(pending),flush=True)
