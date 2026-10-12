"""Exercise the actual release CLIs against controlled repository copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

import pytest

SOURCE = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(SOURCE, tmp_path, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('.git', '.venv', '.superpowers',
                                                  '__pycache__', '.pytest_cache', 'dist', 'artifacts'))
    return tmp_path


def run(repo, script, *args):
    return subprocess.run([sys.executable, str(repo/'scripts'/script), *args],
                          cwd=repo, capture_output=True, text=True, encoding='utf-8')


def change_json(path, key, value):
    data = json.loads(path.read_text(encoding='utf-8'))
    data[key] = value
    path.write_text(json.dumps(data), encoding='utf-8')


def test_tag_mismatch_blocks_release(repo):
    result = run(repo, 'validate_package.py', '--offline', '--tag', 'v9.9.9')
    assert result.returncode != 0, result.stdout
    assert 'tag' in result.stderr.lower()


def test_metadata_mismatch_blocks_release(repo):
    change_json(repo/'release.json', 'plugin_version', '0.2.0')
    result = run(repo, 'validate_package.py', '--offline')
    assert result.returncode != 0, result.stdout
    assert 'version' in result.stderr.lower()


def test_dependency_mismatch_blocks_release(repo):
    change_json(repo/'release.json', 'scrapling_version', '0.4.16')
    result = run(repo, 'validate_package.py', '--offline')
    assert result.returncode != 0, result.stdout
    assert 'pin' in result.stderr.lower()


def test_example_pin_mismatch_blocks_release(repo):
    path = repo/'examples/fastmcp-research/pyproject.toml'
    path.write_text(path.read_text().replace('0.4.15', '0.4.16'), encoding='utf-8')
    result = run(repo, 'validate_package.py', '--offline')
    assert result.returncode != 0, result.stdout
    assert 'example' in result.stderr.lower()


def test_offline_validation_is_labelled_and_accepts_correct_tag(repo):
    result = run(repo, 'validate_package.py', '--offline', '--tag', 'v0.1.1')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['schema_validation'] == 'skipped_offline'


def test_packaging_uses_new_version_and_preserves_release_content(repo):
    change_json(repo/'release.json', 'plugin_version', '0.2.0')
    for relative in ['plugins/scrapling-codex/plugin.json',
                     'plugins/scrapling-codex/.codex-plugin/plugin.json']:
        change_json(repo/relative, 'version', '0.2.0')
    path = repo/'pyproject.toml'
    path.write_text(path.read_text().replace('version = "0.1.1"', 'version = "0.2.0"'))
    (repo/'.env').write_text('LOCAL_SECRET=do-not-package')
    (repo/'docs/.env').write_text('NESTED_SECRET=do-not-package')
    (repo/'docs/private.key').write_text('do-not-package')
    result = run(repo, 'package_release.py')
    assert result.returncode == 0, result.stderr
    target = repo/'dist/scrapling-codex-local-marketplace-0.2.0.zip'
    assert target.exists(), 'Archive version was hardcoded instead of reading metadata'
    with ZipFile(target) as archive:
        names = {name.split('/', 1)[1] for name in archive.namelist()}
        assert '.agents/plugins/marketplace.json' in names
        assert 'plugins/scrapling-codex/.mcp.json' in names
        assert 'uv.lock' in names
        assert 'UPGRADING.md' in names
        assert 'tests/test_release_tools.py' in names
        assert not any(name.endswith(('.env', '.key')) for name in names)
        assert archive.testzip() is None
    with ZipFile(repo/'dist/scrapling-codex-0.2.0.zip') as archive:
        assert archive.read('scrapling-codex/.mcp.json') == (repo/'plugins/scrapling-codex/.mcp.json').read_bytes()


def test_packager_refuses_inconsistent_source(repo):
    change_json(repo/'release.json', 'plugin_version', '0.2.0')
    result = run(repo, 'package_release.py')
    assert result.returncode != 0, 'Packaging must validate before publishing misleading ZIPs'
