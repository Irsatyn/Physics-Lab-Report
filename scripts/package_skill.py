"""Build a portable install archive containing only the physics-lab-report skill."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]

def package(output):
    skill = ROOT / 'physics-lab-report'
    files = sorted(p for p in skill.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.suffix != '.pyc')
    if not (skill / 'SKILL.md').is_file():
        raise ValueError('Missing SKILL.md')
    output = Path(output).resolve()
    if output == skill or skill in output.parents:
        raise ValueError('Archive must be outside the skill directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for p in files:
            archive.write(p, p.relative_to(ROOT).as_posix())
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {p.relative_to(ROOT).as_posix() for p in files}
        for p in files:
            assert archive.read(p.relative_to(ROOT).as_posix()) == p.read_bytes()
    print(f'Verified archive: {output.name} ({len(files)} files)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'physics-lab-report.zip')
    package(parser.parse_args().output)
