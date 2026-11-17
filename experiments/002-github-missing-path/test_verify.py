"""Synthetic fixture tests; no network. Usage: python test_verify.py NEW_OUTPUT_DIR"""
import copy,hashlib,json,pathlib,shutil,subprocess,sys
E=pathlib.Path(__file__).resolve().parent;OUT=pathlib.Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=False)
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def manifest(e):save(e/'manifest.json',{p.relative_to(e).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(e.rglob('*')) if p.is_file() and p!=e/'manifest.json'})
def load(e):return json.loads((e/'observations.json').read_text())
def mutation(e,name):
 d=load(e)
 if name=='empty':d['records']=[]
 elif name=='missing_case':d['records'].pop()
 elif name=='both_payload_missing':
  for i in (0,2):d['records'][i]['file_payload']=None
 elif name=='wrong_ref':d['records'][0]['commit']='0'*40
 elif name=='wrong_path':d['records'][1]['path']='README.md'
 elif name=='size':d['records'][0]['file_payload']['bytes']=0
 elif name=='sha':d['records'][0]['file_payload']['sha256']='0'*64
 elif name=='status_guessed':d['records'][1]['http_status']=404;d['records'][1]['http_status_provided']=True
 elif name=='classification':d['records'][1]['observation']='success'
 elif name=='error_as_file':d['records'][1]['file_payload']={'file':'raw/A-M-1.json','bytes':0,'sha256':'0'*64,'git_blob':'0'*40}
 elif name=='bool_attempt':d['records'][0]['attempt']=True
 elif name=='raw_body_changed':
  (e/'raw/A-N-1.file').write_bytes(b'changed')
 elif name=='raw_missing':(e/'raw/A-M-1.json').unlink()
 elif name in ('unknown_valid','unknown_false_pass'):
  r=d['records'][3];raw=json.loads((e/r['raw_record']).read_text());raw.update(exit_code=28,stdout='000',stderr='curl: (28) synthetic timeout',http_status_provided=False,http_status=None,response_body_bytes=0,body_file_exists=False);save(e/r['raw_record'],raw)
  r.update(exit_code=28,http_status_provided=False,http_status=None,observation='communication_failure',result='UNKNOWN',error=raw['stderr'],reason='Synthetic bounded timeout, not a measured network event.');d['experiment_result']='UNKNOWN' if name=='unknown_valid' else 'PASS'
 elif name in ('missing_normal_valid_unknown','both_normal_missing_false_pass'):
  for i in (0,2):
   r=d['records'][i];raw=json.loads((e/r['raw_record']).read_text())
   if i==0:raw['response']={'isError':True,'structuredContent':{'error':'Synthetic generic error','error_code':'GENERIC'}};r.update(error='Synthetic generic error',observation='general_error',result='UNKNOWN',file_payload=None)
   else:raw.update(exit_code=28,stdout='000',stderr='synthetic timeout',http_status_provided=False,http_status=None,response_body_bytes=0,body_file_exists=False);r.update(exit_code=28,http_status_provided=False,http_status=None,error='synthetic timeout',observation='communication_failure',result='UNKNOWN',file_payload=None)
   save(e/r['raw_record'],raw)
  d['normal_comparison']=None;d['experiment_result']='UNKNOWN' if name=='missing_normal_valid_unknown' else 'PASS'
 elif name in ('a_tool_missing','a_tool_wrong','b_method_wrong','b_source_wrong'):
  i=0 if name.startswith('a_') else 2;r=d['records'][i];raw=json.loads((e/r['raw_record']).read_text())
  if name=='a_tool_missing':del raw['tool']
  elif name=='a_tool_wrong':raw['tool']='different_tool'
  elif name=='b_source_wrong':raw['source']='https://example.invalid/other'
  else:
   raw['command'][raw['command'].index('--request')+1]='POST';r['tool_or_command']=raw['command']
  save(e/r['raw_record'],raw)
 elif name=='plan_changed':(e/'PLAN.md').write_text('altered plan')
 elif name=='manifest_missing_entry':pass
 elif name=='hidden_extra':(e/'.extra').write_text('unexpected');return
 elif name=='normal':pass
 else:raise ValueError(name)
 save(e/'observations.json',d)
 manifest(e)
 if name=='manifest_missing_entry':
  m=json.loads((e/'manifest.json').read_text());del m['PLAN.md'];save(e/'manifest.json',m)
rows=[]
for name in ['normal','empty','missing_case','both_payload_missing','wrong_ref','wrong_path','size','sha','status_guessed','classification','error_as_file','bool_attempt','raw_body_changed','raw_missing','unknown_valid','unknown_false_pass','missing_normal_valid_unknown','both_normal_missing_false_pass','plan_changed','manifest_missing_entry','hidden_extra','a_tool_missing','a_tool_wrong','b_method_wrong','b_source_wrong']:
 p=OUT/name;shutil.copytree(E,p);mutation(p,name)
 run=subprocess.run([sys.executable,str(p/'verify.py')],capture_output=True,text=True)
 expect=name in {'normal','unknown_valid','missing_normal_valid_unknown'}
 row={'case':name,'synthetic':True,'expected_accept':expect,'exit_code':run.returncode,'matches_expectation':(run.returncode==0)==expect,'stdout':run.stdout,'stderr':run.stderr};rows.append(row)
save(OUT/'results.json',rows);print(f'{sum(r["matches_expectation"] for r in rows)}/{len(rows)} expected outcomes')
if not all(r['matches_expectation'] for r in rows):sys.exit(1)
