"""Check exact new-stage artifact set; this is not original-evidence authenticity."""
import pathlib
import sys
sys.dont_write_bytecode = True
from verify import load, require, sha, check_lock
D=pathlib.Path(__file__).resolve().parent
try:
    require(not any(p.is_symlink() for p in D.rglob('*')), 'SYMLINK')
    manifest=load(D/'manifest.json')
    paths={p.relative_to(D).as_posix():p for p in D.rglob('*') if p.is_file() and p != D/'manifest.json'}
    require(paths and set(paths)==set(manifest), 'ARTIFACT_SET_MISMATCH')
    for name,path in paths.items():
        require(not path.is_symlink(), 'SYMLINK')
        raw=path.read_bytes(); m=manifest[name]
        require(type(m['size']) is int and m['size']==len(raw) and m['sha256']==sha(raw), 'ARTIFACT_CHANGED:'+name)
    check_lock()
    print('PASS artifact integrity; independent review and real experiment NOT_TESTED')
except Exception as e:
    print('FAIL:',str(e));sys.exit(1)
