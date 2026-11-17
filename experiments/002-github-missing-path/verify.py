"""Offline evidence-contract verification, never a network measurement."""
import base64, datetime, hashlib, json, pathlib, re, sys
E = pathlib.Path(__file__).resolve().parent
REPO = 'tetsujisugimori-coder/chatGPT-lab'
REF = '3e559a5a12c087ad22d3e1cc146d3aad0866ba33'
TREE = '8fa307eb94c1bdfe98bb0afc34cc0cbf01473742'
PLAN = 'd4a337f922eb698fa474f56ee9189023c1d0859f'
MISSING = 'experiments/002-github-missing-path/__intentionally_absent_20261117__.txt'
CASES = ['A-N', 'A-M', 'B-N', 'B-M']

def need(ok, why):
    if not ok: raise ValueError(why)

def read(e, name):
    p = pathlib.PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts, 'unsafe evidence path')
    return (e/name).read_bytes()

def jread(e, name): return json.loads(read(e, name))

def dig(b):
    return {'bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest(),
            'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}

def stamp(s):
    need(type(s) is str, 'timestamp type')
    t = datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
    need(t.tzinfo is not None, 'timestamp timezone')
    return t

def classify(e, r, raw):
    """Derive observation from saved response, not the submitted PASS label."""
    payload = None
    if r['route']=='A':
        resp = raw['response']; need(type(resp) is dict, 'A response')
        sc = resp.get('structuredContent', {})
        if resp.get('isError') is True:
            error = sc.get('error')
            need(type(error) is str and bool(error), 'A error evidence')
            need('content' not in sc, 'error mixed with file payload')
            kind = 'explicit_missing' if sc.get('error_code')=='NOT_FOUND' and sc.get('error_data',{}).get('message')=='Not Found' else 'general_error'
            if sc.get('error_code') in {'FORBIDDEN','UNAUTHORIZED','PERMISSION_DENIED','UNSUPPORTED'}:kind='permission_or_feature_constraint'
        else:
            need(resp.get('isError') is False and sc.get('encoding')=='base64', 'A successful encoding')
            need(type(sc.get('content')) is str, 'A content absent')
            payload=base64.b64decode(''.join(sc['content'].split()), validate=True)
            need(sc.get('sha')==dig(payload)['git_blob'], 'A response blob')
            kind='success';error=None
        need(r['http_status'] is None and r['http_status_provided'] is False and r['exit_code'] is None, 'A transport status unprovided')
        need(r['tool_or_command']=='mcp__codex_apps__github_fetch_file' and raw['tool']==r['tool_or_command'], 'A tool')
    else:
        need(type(raw['exit_code']) is int, 'B exit type')
        for key in ('exit_code','http_status','http_status_provided'):need(r[key]==raw[key] and type(r[key]) is type(raw[key]), 'B status source '+key)
        need(type(raw['http_status_provided']) is bool, 'B status bool')
        if raw['http_status_provided']:
            need(type(raw['http_status']) is int and 100<=raw['http_status']<=599 and raw['stdout']==str(raw['http_status']), 'B HTTP evidence')
        else:need(raw['http_status'] is None, 'B absent HTTP')
        need(raw['source']==r['source'], 'B raw source')
        cmd=raw['command'];need(r['tool_or_command']==cmd and type(cmd) is list,'B command')
        need(cmd[:2]==['curl','-q'] and cmd[cmd.index('--connect-timeout')+1]=='10' and cmd[cmd.index('--max-time')+1]=='25', 'B finite deadline')
        need(cmd.count('--request')==1 and cmd[cmd.index('--request')+1]=='GET', 'B GET method')
        need(cmd[-1]==r['source'] and not any('authorization' in x.lower() for x in cmd),'B URL/auth')
        b=read(e, 'raw/'+raw['response_body_file']) if raw['body_file_exists'] else b''
        need(len(b)==raw['response_body_bytes'], 'B response bytes')
        if raw['exit_code']!=0:
            kind='communication_failure';error=raw['stderr'];need(type(error) is str and bool(error),'B transport error')
        else:
            obj=json.loads(b); status=raw['http_status']
            if status==200:
                need(obj.get('encoding')=='base64' and obj.get('path')==r['path'] and obj.get('type')=='file', 'B file identity')
                payload=base64.b64decode(''.join(obj['content'].split()),validate=True)
                need(obj['sha']==dig(payload)['git_blob'] and obj['size']==len(payload),'B content digest')
                kind='success';error=None
            elif status==404 and obj.get('message')=='Not Found':
                need('content' not in obj,'B error contains file');kind='explicit_missing';error=obj['message']
            else:kind='permission_or_feature_constraint' if status in (401,403) else 'general_error';error=obj.get('message')
    need(r['error']==error, 'normalized error mismatch')
    return kind,payload

def verify(e=E):
    d=jread(e,'observations.json');need(type(d) is dict and d['schema_version']==1,'schema')
    for k,v in [('repository',REPO),('target_commit',REF),('target_tree',TREE),('plan_commit',PLAN)]:need(d[k]==v,'fixed '+k)
    prereg=jread(e,'preregistration.json');need(prereg['plan_commit']==PLAN and prereg['target_commit']==REF and prereg['target_tree']==TREE,'prereg refs')
    need(prereg['committed_before_measurement'] is True and prereg['readback_exact_before_measurement'] is True,'prereg gate')
    pb=read(e,'PLAN.md');need(dig(pb)['sha256']==prereg['plan_sha256'] and dig(pb)['git_blob']==prereg['plan_blob'],'plan changed')
    tree=jread(e,'target-tree.json');need(tree['sha']==TREE and tree['truncated'] is False,'tree complete')
    entries=tree['tree'];need(type(entries) is list and len(entries)==12 and len({x['path'] for x in entries})==12,'tree set')
    need(MISSING not in {x['path'] for x in entries}, 'missing target exists')
    entry=next(x for x in entries if x['path']=='README.md');need(entry['type']=='blob','README blob')
    rows=d['records'];need(type(rows) is list and bool(rows),'empty records')
    need([r['case_id'] for r in rows if r['attempt']==1]==CASES, 'case set/order')
    need(len(rows)<=8,'retry total')
    previous=stamp(prereg['commit_created_at']); last={}; payloads={}; outcomes={}
    for r in rows:
        fields={'case_id','route','attempt','repository','commit','path','started_at','ended_at','source','tool_or_command','raw_record','http_status_provided','http_status','exit_code','observation','result','reason','file_payload','error'}
        need(type(r) is dict and fields<=r.keys(),'required fields')
        cid=r['case_id'];need(cid in CASES and r['route']==cid[0],'case route')
        need(type(r['attempt']) is int and r['attempt'] in (1,2),'attempt type')
        if cid in last:need(r['attempt']==2 and last[cid]['attempt']==1 and last[cid]['observation']=='communication_failure','retry eligibility')
        else:need(r['attempt']==1,'first attempt')
        path='README.md' if cid.endswith('N') else MISSING
        need(r['repository']==REPO and r['commit']==REF and r['path']==path,'fixed target')
        source=f'https://github.com/{REPO}/blob/{REF}/{path}' if cid[0]=='A' else f'https://api.github.com/repos/{REPO}/contents/{path}?ref={REF}'
        need(r['source']==source,'source')
        start,end=stamp(r['started_at']),stamp(r['ended_at']);need(previous<=start<=end,'chronology');previous=end
        need(type(r['reason']) is str and bool(r['reason']),'reason')
        raw=jread(e,r['raw_record'])
        for k in ['case_id','route','attempt','repository','commit','path','started_at','ended_at']:need(raw[k]==r[k] and type(raw[k]) is type(r[k]),'raw attribution '+k)
        kind,payload=classify(e,r,raw);need(r['observation']==kind,'classification evidence')
        if payload is None:need(r['file_payload'] is None,'error is not file content')
        else:
            fp=r['file_payload'];need(type(fp) is dict and set(fp)=={'file','bytes','sha256','git_blob'},'payload fields')
            need(type(fp['bytes']) is int and fp['bytes']>=0,'payload size type')
            need(read(e,fp['file'])==payload and {k:fp[k] for k in dig(payload)}==dig(payload),'payload digest/bytes')
        result=('FAIL' if cid.endswith('M') and kind=='success' else 'BLOCKED' if kind=='permission_or_feature_constraint' else 'UNKNOWN' if kind in {'communication_failure','general_error'} else 'UNKNOWN' if cid.endswith('N') and kind!='success' else 'PASS')
        need(r['result']==result,'case result evidence')
        last[cid]=r;payloads[cid]=payload;outcomes[cid]=result
    need(set(last)==set(CASES),'all cases required')
    normal=payloads['A-N'];other=payloads['B-N'];comparison=d['normal_comparison']
    comparable=normal is not None and other is not None
    matched=comparable and normal==other and dig(normal)['git_blob']==entry['sha'] and len(normal)==entry['size']
    if comparable:
        need(type(comparison) is dict and set(comparison)=={'equal_bytes','bytes','sha256','git_blob'},'comparison fields')
        need(type(comparison['equal_bytes']) is bool and comparison['equal_bytes']==matched,'comparison match')
        need(type(comparison['bytes']) is int and {k:comparison[k] for k in dig(normal)}==dig(normal),'comparison digest')
    else:need(comparison is None,'missing comparison cannot match')
    overall='FAIL' if 'FAIL' in outcomes.values() or (comparable and not matched) else 'PASS' if matched and all(x=='PASS' for x in outcomes.values()) and last['A-M']['observation']==last['B-M']['observation']=='explicit_missing' else 'UNKNOWN'
    need(d['experiment_result']==overall,'experiment result evidence')
    files=set()
    for p in e.rglob('*'):
        need(not p.is_symlink(),'symlink')
        if p.is_file() and p.name!='manifest.json':files.add(p.relative_to(e).as_posix())
        elif p.is_file():need(p==e/'manifest.json','nested manifest')
    required={'PLAN.md','RESULTS.md','observations.json','verify.py','target-tree.json','preregistration.json','test_verify.py','verification-results.json'}
    need(required<=files,'mandatory file set')
    m=jread(e,'manifest.json');need(type(m) is dict and set(m)==files,'manifest set')
    for name,row in m.items():
        b=read(e,name);need(type(row) is dict and set(row)=={'bytes','sha256'} and type(row['bytes']) is int,'manifest schema')
        need(row=={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},'manifest digest '+name)
    return {'record_integrity':'PASS','network_experiment':overall,'attempts':len(rows),'manifest_files':len(files)}

if __name__=='__main__':
    try:print(json.dumps(verify(),ensure_ascii=False))
    except (ValueError,KeyError,TypeError,OSError,StopIteration) as err:
        print('FAIL:',err);sys.exit(1)
