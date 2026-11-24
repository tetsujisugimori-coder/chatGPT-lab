"""Exact-set/byte-lock counterexamples on new disposable copies; no network."""
import pathlib,shutil,subprocess,sys,json
D=pathlib.Path(__file__).resolve().parent
out=pathlib.Path(sys.argv[1]).resolve()
if out == D or D in out.parents:
    print('BLOCKED: output directory must be outside source tree', file=sys.stderr)
    sys.exit(2)
out.mkdir(parents=True,exist_ok=False)
rows=[]
for case in ['normal','changed','missing','extra','nested_manifest']:
    p=out/case;shutil.copytree(D,p)
    if case=='changed':(p/'INSTRUCTIONS.txt').write_text('tampered')
    if case=='missing':(p/'INSTRUCTIONS.txt').unlink()
    if case=='extra':(p/'.unexpected').write_text('extra')
    if case=='nested_manifest':(p/'fixtures/manifest.json').write_text('{}')
    r=subprocess.run([sys.executable,'-B',str(p/'check_artifacts.py')],capture_output=True,text=True,timeout=15)
    rows.append({'case':case,'synthetic':True,'expected_accept':case=='normal','exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'matches_expectation':(r.returncode==0)==(case=='normal')})
(out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(sum(r['matches_expectation'] for r in rows),'/',len(rows))
sys.exit(0 if all(r['matches_expectation'] for r in rows) else 1)
