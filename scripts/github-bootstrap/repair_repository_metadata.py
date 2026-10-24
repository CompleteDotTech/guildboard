"""Fill missing repo metadata; optionally apply reviewed planned milestone changes.
Never removes labels, assigns contributors, changes issue state or replaces issue bodies.
"""
from api import *
import argparse,time
p=argparse.ArgumentParser();p.add_argument('--apply-planned-milestones',action='store_true');p.add_argument('--apply-planned-release',action='store_true');args=p.parse_args();m=json.loads((ROOT/'planning/guildboard-backlog.json').read_text());s=json.loads(STATE.read_text());repo=s['repo'];changed=[];drift=[]
rows=[];page=1
while True:
 r=api(f'repos/{repo}/issues?state=all&per_page=100&page={page}');rows+=r
 if len(r)<100:break
 page+=1
live={r['number']:r for r in rows if 'pull_request' not in r}
for x in m['items']:
 if not x.get('github') or x['github']['number'] not in live:continue
 r=live[x['github']['number']];labels={v['name'] for v in r['labels']};update={}
 if set(x['labels'])-labels:update['labels']=sorted(labels|set(x['labels']))
 if args.apply_planned_release:
  expected={v for v in x['labels'] if v.startswith('release:')}
  if {v for v in labels if v.startswith('release:')}!=expected:update['labels']=sorted({v for v in labels if not v.startswith('release:')}|expected|set(x['labels']))
 milestone=s['milestones'][x['milestone']]
 if not r['milestone']:update['milestone']=milestone
 elif r['milestone']['number']!=milestone:
  if args.apply_planned_milestones:update['milestone']=milestone
  else:drift.append({'id':x['id'],'planned':x['milestone'],'live':r['milestone']['title']})
 if update:
  api(f"repos/{repo}/issues/{r['number']}",'PATCH',update);changed.append({'id':x['id'],'fields':list(update)});print('Repaired repository metadata',x['id'],flush=True);time.sleep(1.2)
if args.apply_planned_release:
 fields={f['name']:f for f in api('users/'+s['owner']+'/projectsV2/'+str(s['project']['number'])+'/fields?per_page=100')}
 field=fields['Release Target'];options={(o['name']['raw'] if isinstance(o['name'],dict) else o['name']):o['id'] for o in field['options']}
 project_items={};after=None
 while True:
  r=gql('query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){nodes{fullDatabaseId content{... on Issue{id}} fieldValues(first:30){nodes{... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}}}}} pageInfo{hasNextPage endCursor}}}}}',id=s['project']['id'],after=after)['node']['items']
  for v in r['nodes']:
   if v.get('content') and v['content'].get('id'):project_items[v['content']['id']]=v
  if not r['pageInfo']['hasNextPage']:break
  after=r['pageInfo']['endCursor']
 updates=[]
 for x in m['items']:
  if not x.get('github'):continue
  item=project_items.get(x['github']['id'])
  if not item:continue
  vals={v['field']['name']:v['name'] for v in item['fieldValues']['nodes'] if v}
  if vals.get('Release Target')!=x['fields']['Release Target']:updates.append((x,item))
 import concurrent.futures
 def apply_release(row):
  x,item=row;api('users/'+s['owner']+'/projectsV2/'+str(s['project']['number'])+'/items/'+str(item['fullDatabaseId']),'PATCH',{'fields':[{'id':field['id'],'value':options[x['fields']['Release Target']]}]});return x['id']
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for id in pool.map(apply_release,updates):print('Aligned reviewed release scope',id,flush=True)
save(ROOT/'planning/audit/repository-metadata-repair.json',{'changed':changed,'preserved_milestone_drift':drift})
print('Changed',len(changed),'preserved drift',len(drift),flush=True)
