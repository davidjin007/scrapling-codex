"""Build local ZIPs from source, including hidden files, and inspect contents."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root=Path(__file__).resolve().parents[1]
dist=root/'dist'
dist.mkdir(exist_ok=True)
excluded={'.venv','__pycache__','.pytest_cache','.git','.superpowers','node_modules'}


def files_under(base):
    for path in sorted(base.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlinks are not included: {path}')
        if path.is_file() and not any(part in excluded for part in path.relative_to(root).parts) and path.suffix!='.pyc':
            yield path


def build(filename, prefix, files, relative_to, required):
    target=dist/filename
    with ZipFile(target,'w',ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path,f'{prefix}/{path.relative_to(relative_to).as_posix()}')
    with ZipFile(target) as archive:
        names=set(archive.namelist())
        assert archive.testzip() is None
        assert all(f'{prefix}/{name}' in names for name in required)
        assert not any(part in excluded for name in names for part in Path(name).parts)
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        result={'archive':target.name,'files':len(names),'bytes':target.stat().st_size,'sha256':digest,
                'zip_crc_valid':True,'required_hidden_files_present':True}
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n',encoding='ascii')
    return result


plugin=root/'plugins/scrapling-codex'
workshop_files=[root/'README.md',root/'.gitignore']
for folder in ['.agents','plugins','docs','examples','scripts']:
    workshop_files.extend(files_under(root/folder))
results=[
    build('scrapling-codex-local-marketplace-0.1.1.zip','scrapling-codex-local-marketplace',workshop_files,root,
          ['.agents/plugins/marketplace.json','plugins/scrapling-codex/.codex-plugin/plugin.json',
           'plugins/scrapling-codex/.mcp.json','examples/fastmcp-research/uv.lock']),
    build('scrapling-codex-0.1.1.zip','scrapling-codex',files_under(plugin),plugin,
          ['plugin.json','mcp.json','.codex-plugin/plugin.json','.mcp.json','skills/scrapling-web-crawl/SKILL.md'])
]
(dist/'release-checks.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
