"""Run versioned synthetic fixtures offline. Output directory must be new.
Inputs are reconstructed from base + explicit JSON patches, retained separately.
No live adapters, no network, no production files modified.
"""
import copy
import datetime
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys

D = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from verify import load, require, sha


def apply(base, patches):
    value = copy.deepcopy(base)
    for change in patches:
        path = change['path'].split('/')[1:]
        require(path and all(x not in ('', '..') for x in path), 'bad fixture patch')
        node = value
        for key in path[:-1]:
            node = node[int(key)] if isinstance(node, list) else node[key]
        key = int(path[-1]) if isinstance(node, list) else path[-1]
        require(change['op'] in ('replace', 'remove'), 'unknown patch operation')
        if change['op'] == 'remove':
            del node[key]
        else:
            require((type(node) is list and 0 <= key < len(node)) or key in node, 'replace missing field')
            node[key] = change['value']
    return value


def main():
    out = pathlib.Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    cases, base = load(D/'fixtures/cases.json'), load(D/'fixtures/base.json')
    require(cases and len({c['id'] for c in cases}) == len(cases), 'fixture case set')
    rows = []
    for c in cases:
        packet = apply(base, c['patches'])
        raw = (json.dumps(packet, ensure_ascii=False, indent=2)+'\n').encode()
        path = out / (c['id']+'.json')
        path.write_bytes(raw)
        run = subprocess.run([sys.executable, '-B', str(D/'verify.py'), str(path)],
                             capture_output=True, text=True, timeout=15,
                             env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
        actual = json.loads(run.stdout)
        expected = c['expected']
        ok = (actual['record_validation'] == expected['record_validation'] and
              actual['comparison_decision'] == expected['comparison_decision'] and
              actual['reason'].startswith(expected['reason_prefix']) and
              actual['experiment_outcome'] == 'NOT_TESTED' and
              (expected['record_validation'] != 'PASS' or actual.get('ranking_status') == 'NOT_TESTED') and
              run.returncode == {'PASS':0,'FAIL':1,'BLOCKED':2}[expected['record_validation']] and
              not run.stderr)
        if 'synthetic_run_outcomes' in expected:
            ok &= actual.get('synthetic_run_outcomes') == expected['synthetic_run_outcomes']
        rows.append({'id':c['id'],'title':c['title'],'synthetic':True,'input_size':len(raw),
                     'input_sha256':sha(raw),'expected':expected,'actual':actual,
                     'matches_expectation':ok,'command':'python -B verify.py <case-input.json>',
                     'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
    report = {'scope':'offline synthetic record validation, not product testing',
              'started_from_lock_sha256':sha((D/'protocol.lock.json').read_bytes()),
              'fixtures_sha256':sha((D/'fixtures/cases.json').read_bytes()),
              'base_sha256':sha((D/'fixtures/base.json').read_bytes()),
              'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'environment':{'python':platform.python_version(),'os':platform.system(),'machine':platform.machine()},
              'total':len(rows),'matched':sum(r['matches_expectation'] for r in rows),
              'failed':sum(not r['matches_expectation'] for r in rows),'rows':rows}
    (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'{report["matched"]}/{report["total"]} expectations matched; real experiment NOT_TESTED')
    for row in rows:
        if not row['matches_expectation']:
            print(row['id'], row['actual'])
    return 0 if report['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
