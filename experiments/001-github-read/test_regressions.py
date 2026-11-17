"""Offline mutation tests. Usage: python test_regressions.py BEFORE AFTER OUTPUT_DIR.
Fixtures are new copies, retained; no network calls. Each content mutation renews
manifest so content rejection is not merely a stale hash rejection.
"""
import copy, hashlib, json, pathlib, shutil, subprocess, sys
before, after, out = map(lambda x:pathlib.Path(x).resolve(), sys.argv[1:])
out.mkdir(parents=True, exist_ok=False)
E='experiments/001-github-read'; M=E+'/manifest.json'
def manifest(p):
    files={x.relative_to(p).as_posix():x for x in p.rglob('*') if x.is_file() and '.git' not in x.relative_to(p).parts and x.relative_to(p).as_posix()!=M}
    (p/M).write_text(json.dumps({k:{'bytes':len(v.read_bytes()),'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for k,v in sorted(files.items())},indent=2)+'\n')
def command(p,*args):
    return subprocess.run(args,cwd=p,text=True,capture_output=True)
# Fixed named cases are applied identically to both verifier versions.
cases=[('normal',True,None),('checkout',True,None),('worktree',True,None),('missing_file',False,None),('changed_file',False,None),('size',False,None),('sha',False,None),('hidden_extra',False,None),('nested_manifest',False,None)]
def add(name,func,ok=False): cases.append((name,ok,func))
for index in range(3):
    sample=json.loads((before/E/'observations.json').read_text())['records'][index]['connector']['snapshot']
    paths=[(k,) for k in sample]
    if index==2: paths += [(k,s) for k in ('base','head') for s in ('ref','sha')]
    for path in paths:
        for side in ('connector','comparison','both'):
            def missing(d,i=index,path=path,side=side):
                for s in (('connector','comparison') if side=='both' else (side,)):
                    v=d['records'][i][s]['snapshot']
                    for key in path[:-1]: v=v[key]
                    del v[path[-1]]
            add(f'G{index+1:02}_missing_{"_".join(path)}_{side}',missing)
        def badtype(d,i=index,path=path):
            for s in ('connector','comparison'):
                v=d['records'][i][s]['snapshot']
                for key in path[:-1]: v=v[key]
                v[path[-1]]=[]
        add(f'G{index+1:02}_type_{"_".join(path)}',badtype)
    for variant in ('empty','partial','integer','string','false'):
        def matches(d,i=index,v=variant):
            m=d['records'][i]['matches']; key=next(iter(m))
            if v=='empty': m.clear()
            elif v=='partial': del m[key]
            else: m[key]={'integer':1,'string':'true','false':False}[v]
        add(f'G{index+1:02}_matches_{variant}',matches)
    def mismatch(d,i=index): d['records'][i]['comparison']['snapshot']['body_utf8' if i==0 else 'body']+='x'
    add(f'G{index+1:02}_mismatch',mismatch)
for i in (1,2):
    def empty(d,i=i):
        for s in ('connector','comparison'): d['records'][i][s]['snapshot']['body']=''
    add(f'G{i+1:02}_empty_body',empty,True)
def exploit(d):
    for i in (1,2):
        r=d['records'][i]
        for s in ('connector','comparison'): r[s]['snapshot']={'number':r[s]['snapshot']['number']}
        r['matches']={}
add('review_number_only_empty_matches',exploit)
rows=[]
for version, source in [('before',before),('after',after)]:
    for name,expected,mutate in cases:
        p=out/version/name; shutil.copytree(source,p)
        if mutate:
            d=json.loads((p/E/'observations.json').read_text());mutate(d)
            (p/E/'observations.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');manifest(p)
        elif name in ('checkout','worktree'):
            assert command(p,'git','init','-q').returncode==0
            assert command(p,'git','add','.').returncode==0
            assert command(p,'git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','offline fixture').returncode==0
            if name=='worktree':
                linked=out/version/'linked-worktree'
                assert command(p,'git','worktree','add','--detach',str(linked),'HEAD').returncode==0
                p=linked
        elif name=='missing_file': (p/'docs/research-map.md').unlink()
        elif name=='changed_file': (p/'docs/research-map.md').write_text('changed fixture')
        elif name in ('size','sha'):
            m=json.loads((p/M).read_text());m['README.md']['bytes' if name=='size' else 'sha256']=0 if name=='size' else '0'*64;(p/M).write_text(json.dumps(m))
        elif name=='hidden_extra': (p/'.unexpected').write_text('fixture')
        elif name=='nested_manifest': (p/'docs/manifest.json').write_text('{}')
        run=command(p,sys.executable,E+'/verify.py')
        rows.append({'version':version,'case':name,'expected_accept':expected,'exit_code':run.returncode,'accepted':run.returncode==0,'matches_expectation':(run.returncode==0)==expected,'stdout':run.stdout,'stderr':run.stderr.replace(str(out),'<fixture>')})
(out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for v in ('before','after'):
    group=[r for r in rows if r['version']==v];print(v,len(group),'expected matched',sum(r['matches_expectation'] for r in group))
assert all(r['matches_expectation'] for r in rows if r['version']=='after')
