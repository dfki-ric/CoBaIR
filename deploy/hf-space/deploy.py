"""Upload the CoBaIR web GUI to its Hugging Face Docker Space.

Usage: `python deploy/hf-space/deploy.py <space id> <version>`, e.g. `dfki-ric/cobair-editor 5.0.0`.
Needs `huggingface_hub`, the token in `HF_TOKEN` and the wheel in `dist/`.
"""

# System imports
import shutil
import sys
import tempfile
from pathlib import Path

# 3rd party imports

# local imports

# end file header
__author__ = 'Adrian Lubitz'

SPACE_DIR = Path(__file__).parent


def stage(target: Path, dist: Path) -> None:
    """Put the files of the Space into a directory.

    Args:
        target: The empty directory to fill.
        dist: The directory with the wheel.

    Raises:
        SystemExit: If there is not exactly one wheel.
    """
    wheels = list(dist.glob('cobair-*.whl'))
    if len(wheels) != 1:
        raise SystemExit(f'Expected one cobair wheel in {dist}, found {wheels}')
    for name in ('Dockerfile', 'README.md'):
        shutil.copy(SPACE_DIR / name, target / name)
    (target / 'dist').mkdir()
    shutil.copy(wheels[0], target / 'dist' / wheels[0].name)


def main(space_id: str, version: str) -> None:
    """Create the Space if needed and replace its files.

    Args:
        space_id: `<owner>/<name>` of the Space.
        version: The released version, used in the commit message.
    """
    from huggingface_hub import HfApi  # pylint: disable=import-outside-toplevel

    api = HfApi()
    api.create_repo(space_id, repo_type='space', space_sdk='docker', exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        stage(Path(directory), Path('dist'))
        api.upload_folder(repo_id=space_id, repo_type='space', folder_path=directory,
                          commit_message=f'Deploy cobair {version}',
                          delete_patterns=['dist/*.whl'])
    print(f'Deployed cobair {version} to https://huggingface.co/spaces/{space_id}')


if __name__ == '__main__':
    main(*sys.argv[1:3])
