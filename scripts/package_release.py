"""Build versioned ZIPs from validated source, preserving hidden files."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from validate_package import validate

EXCLUDED = {'.venv', '__pycache__', '.pytest_cache', '.git', '.superpowers',
            'node_modules', 'dist', 'artifacts', '.idea', '.vscode'}


def files_under(root, base):
    for path in sorted(base.rglob('*')):
        parts = path.relative_to(root).parts
        if any(part in EXCLUDED or part.startswith('.env') for part in parts):
            continue
        if path.suffix in {'.pyc', '.key', '.pem'}:
            continue
        if path.is_symlink():
            raise ValueError(f'Symlinks are not included: {path}')
        if path.is_file():
            yield path


def build(dist, filename, prefix, files, relative_to, required):
    target=dist/filename
    with ZipFile(target,'w',ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path,f'{prefix}/{path.relative_to(relative_to).as_posix()}')
    with ZipFile(target) as archive:
        names=set(archive.namelist())
        assert archive.testzip() is None
        assert all(f'{prefix}/{name}' in names for name in required)
        assert not any(part in EXCLUDED for name in names for part in Path(name).parts)
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        result={'archive':target.name,'files':len(names),'bytes':target.stat().st_size,'sha256':digest,
                'zip_crc_valid':True,'required_hidden_files_present':True}
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n',encoding='ascii')
    return result


def package(root: Path, output: Path | None = None) -> list:
    root = root.resolve()
    version = validate(root, schemas=False)['plugin_version']
    dist = output or root/'dist'
    dist.mkdir(parents=True, exist_ok=True)
    plugin = root/'plugins/scrapling-codex'
    files = [root/name for name in ['README.md', 'CHANGELOG.md', 'UPGRADING.md',
             'CONTRIBUTING.md', 'THIRD_PARTY_NOTICES.md', 'release.json', 'pyproject.toml',
             'uv.lock', '.gitignore', '.gitattributes']]
    for folder in ['.agents', '.github', 'plugins', 'docs', 'examples', 'scripts', 'tests']:
        files.extend(files_under(root, root/folder))
    results = [
        build(dist, f'scrapling-codex-local-marketplace-{version}.zip',
              'scrapling-codex-local-marketplace', files, root,
              ['.agents/plugins/marketplace.json', 'plugins/scrapling-codex/.codex-plugin/plugin.json',
               'plugins/scrapling-codex/.mcp.json', 'examples/fastmcp-research/uv.lock', 'uv.lock', 'UPGRADING.md']),
        build(dist, f'scrapling-codex-{version}.zip', 'scrapling-codex', files_under(root, plugin), plugin,
              ['plugin.json', 'mcp.json', '.codex-plugin/plugin.json', '.mcp.json',
               'skills/scrapling-web-crawl/SKILL.md'])
    ]
    (dist/'release-checks.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    return results


if __name__ == '__main__':
    print(json.dumps(package(Path(__file__).resolve().parents[1]), indent=2))
