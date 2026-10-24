"""GitHub transport. Uses gh keyring authentication; never logs credentials."""
import json, subprocess, time, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[2]
STATE=ROOT/'planning/github-state.json'
def save(path,data):
 path=pathlib.Path(path); tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)
def api(path,method='GET',data=None):
 args=['gh','api',path,'--method',method]
 if data is not None: args+=['--input','-']
 for attempt in range(6):
  p=subprocess.run(args,input=json.dumps(data) if data is not None else None,capture_output=True,text=True)
  if p.returncode==0:
   result=json.loads(p.stdout) if p.stdout.strip() else {}
   if not isinstance(result,dict) or not result.get('errors'): return result
  else: result={'stderr':p.stderr,'response':p.stdout}
  (ROOT/'planning/audit/failures.jsonl').open('a').write(json.dumps({'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endpoint':path,'method':method,'error':result})+'\n')
  if any(t in json.dumps(result).lower() for t in ['rate limit','secondary','502','503','timeout']):time.sleep(min(60,2**attempt*5));continue
  raise RuntimeError(json.dumps(result))
 raise RuntimeError('GitHub retry budget exhausted')
def gql(query,**variables):return api('graphql','POST',{'query':query,'variables':variables})['data']
FIELD_FRAGMENT='... on ProjectV2Field{id name dataType} ... on ProjectV2SingleSelectField{id name dataType options{id name color description}}'
def project():
 s=json.loads(STATE.read_text());return gql('query($id:ID!){node(id:$id){... on ProjectV2{id title url number public fields(first:100){nodes{'+FIELD_FRAGMENT+'}} views(first:100){nodes{id number name layout filter configuration{visibleFields(first:100){nodes{'+FIELD_FRAGMENT+'}}}}} workflows(first:100){nodes{id name enabled}} repositories(first:50){nodes{nameWithOwner}}}}}',id=s['project']['id'])['node']
