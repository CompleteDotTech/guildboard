"""Resolve/create this authorized account's repository and copied Project.
Existing state pins the destination; existing private repositories are never published.
The reference's current node ID is resolved read-only before copy, never guessed.
"""
from api import *
TITLE='Guildboard — Engineering & Delivery'
DESCRIPTION='An open-source, real-time moderated whiteboard Discord Activity with collaborative drawing, Discord role-based editing, persistent boards, secure moderation, and GoDaddy self-hosting.'
viewer=gql('query{viewer{id login}}')['viewer'];state=json.loads(STATE.read_text()) if STATE.exists() else {'owner':viewer['login'],'owner_id':viewer['id'],'repo':viewer['login']+'/guildboard'}
if state['owner']!=viewer['login']:raise SystemExit('Initialization is pinned to the authorized account; authenticate as '+state['owner']+'. Existing resources were not changed.')
r=api('repos/'+state['repo']) if subprocess.run(['gh','repo','view',state['repo'],'--json','id'],capture_output=True).returncode==0 else None
if r and r['visibility']!='public':raise SystemExit('Existing private work preserved. Do not publish an existing repository through bootstrap initialization.')
if not r:r=api('user/repos','POST',{'name':'guildboard','private':False,'description':DESCRIPTION,'has_issues':True,'auto_init':False})
projects=[];after=None
while True:
 q=gql('query($after:String){viewer{projectsV2(first:100,after:$after){nodes{id title number url} pageInfo{hasNextPage endCursor}}}}',after=after)['viewer']['projectsV2'];projects+=q['nodes']
 if not q['pageInfo']['hasNextPage']:break
 after=q['pageInfo']['endCursor']
if state.get('project'):
 p=next((p for p in projects if p['id']==state['project']['id']),None)
 if not p:raise SystemExit('Pinned Project is unavailable; preserve mappings and resolve access/deletion before continuing.')
else:
 matches=[p for p in projects if p['title']==TITLE]
 if len(matches)>1:raise SystemExit('Multiple matching Projects; resolve destination explicitly rather than choosing arbitrarily.')
 p=matches[0] if matches else None
 if not p:
  reference=gql('query{organization(login:"Pick-Your-AI"){projectV2(number:1){id title}}}')['organization']['projectV2']
  if not reference:raise SystemExit('Reference Project unavailable; inspect access before creating a replacement configuration.')
  p=gql('mutation($i:CopyProjectV2Input!){copyProjectV2(input:$i){projectV2{id title number url}}}',i={'projectId':reference['id'],'ownerId':viewer['id'],'title':TITLE,'includeDraftIssues':False})['copyProjectV2']['projectV2']
  count=gql('query($id:ID!){node(id:$id){... on ProjectV2{items(first:1){totalCount}}}}',id=p['id'])['node']['items']['totalCount']
  if count:raise SystemExit('Unexpected copied items; inspect the destination before any population. Source remains read-only.')
state.update({'project':p,'repository_id':r['node_id']});save(STATE,state)
print('Resolved existing/new destination:',r['html_url'],p['url'])
