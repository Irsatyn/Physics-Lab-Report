"""Read-only environment inventory; no installs, uploads or MATLAB startup."""
import importlib.util
import json
import shutil
import subprocess
import sys


def main():
    names = ['docx', 'lxml', 'numpy', 'matplotlib', 'pypdfium2']
    paths = dict.fromkeys(p for p in [sys.executable, shutil.which('python')] if p)
    python = []
    code = 'import importlib.util,json; print(json.dumps({m:bool(importlib.util.find_spec(m)) for m in '+repr(names)+'}))'
    for executable in paths:
        try:
            run = subprocess.run([executable, '-c', code], capture_output=True, text=True, timeout=15, check=True)
            python.append({'executable': executable, 'packages': json.loads(run.stdout)})
        except (subprocess.SubprocessError, OSError, ValueError) as exc:
            python.append({'executable': executable, 'error': type(exc).__name__})
    print(json.dumps({'python': python, 'matlab': shutil.which('matlab'),
                      'soffice': shutil.which('soffice'), 'pdftoppm': shutil.which('pdftoppm'),
                      'note': 'Command presence does not prove MATLAB licensing or successful execution'}, indent=2))


if __name__ == '__main__':
    main()
