"""Verify integrity runner refuses unsafe destination before any writes."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

SOURCE = pathlib.Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='stage1a-destination-') as tmp:
        copied = pathlib.Path(tmp) / 'stage1a'
        shutil.copytree(SOURCE, copied)
        child = copied / '__guardrail_output_must_not_exist__'
        for label, output in [('source-itself', copied), ('source-child', child)]:
            result = subprocess.run([sys.executable, '-B', str(copied / 'test_integrity.py'), str(output)],
                                    capture_output=True, text=True, timeout=10)
            assert result.returncode == 2, (label, result.returncode, result.stdout, result.stderr)
            assert 'output directory must be outside source tree' in result.stderr, label
            assert not child.exists(), label
            print(label, 'PASS: rejected without changing copied source')
    return 0


if __name__ == '__main__':
    sys.exit(main())
