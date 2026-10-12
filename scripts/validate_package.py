"""Validate runtime pins and manifests against release.json; never mutate them."""
import argparse
import json
from pathlib import Path
import re
import urllib.request

import jsonschema
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from release_config import load_release


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate(root: Path, schemas: bool = True, tag: str | None = None) -> dict:
    root = root.resolve()
    release = load_release(root)
    version, upstream = release['plugin_version'], release['scrapling_version']
    require(tag is None or tag == f'v{version}', f'Release tag {tag!r} mismatches version {version}')
    plugin = root/'plugins/scrapling-codex'
    portable = read_json(plugin/'plugin.json')
    compat = read_json(plugin/'.codex-plugin/plugin.json')
    for key in ['name', 'version', 'description', 'author', 'keywords']:
        require(portable[key] == compat[key], f'Manifest {key} mismatch')
    require(portable['version'] == version, 'Manifest version mismatches release.json')
    require(portable['name'] == 'scrapling-codex', 'Unexpected plugin identity')
    require(portable['extensions']['com.openai']['interface'] == compat['interface'], 'Interface mismatch')
    require(len(compat['interface']['shortDescription']) <= 30, 'Short description too long')
    require(all(len(p) <= 128 for p in compat['interface']['defaultPrompt']), 'Prompt too long')
    a = read_json(plugin/'mcp.json')['mcpServers']
    b = read_json(plugin/'.mcp.json')['mcpServers']
    require(set(a) == set(b) == {'scrapling_local'}, 'MCP server identity mismatch')
    require({k: v for k, v in a['scrapling_local'].items() if k != 'type'} == b['scrapling_local'],
            'MCP config mismatch')
    server = b['scrapling_local']
    require(server['command'] == 'uvx', 'Unexpected MCP executable')
    require(server['args'] == ['--from', f'scrapling[ai]=={upstream}', 'scrapling-mcp'], 'MCP pin mismatch')
    maintenance = tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))
    require(maintenance['project']['version'] == version, 'Maintenance version mismatch')
    example = tomllib.loads((root/'examples/fastmcp-research/pyproject.toml').read_text(encoding='utf-8'))
    require(f'scrapling[rag]=={upstream}' in example['project']['dependencies'], 'Example pin mismatch')
    for key in ['skills', 'mcpServers']:
        require((plugin/compat[key]).exists(), f'Missing path: {key}')
    skill = plugin/'skills/scrapling-web-crawl/SKILL.md'
    for link in re.findall(r'\]\(([^)]+)\)', skill.read_text(encoding='utf-8')):
        if not link.startswith(('http:', 'https:')):
            require((skill.parent/link).exists(), f'Missing skill reference: {link}')
    require((skill.parent/'references/upstream/LICENSE.txt').exists(), 'Missing upstream license')
    sources = (skill.parent/'references/SOURCES.md').read_text(encoding='utf-8')
    require(f'/Scrapling/tree/v{upstream}' in sources, 'Reference source version mismatch')
    market = read_json(root/'.agents/plugins/marketplace.json')
    require(market['name'] == 'tool-workshop-local', 'Marketplace identity mismatch')
    entries = [p for p in market['plugins'] if p['name'] == 'scrapling-codex']
    require(len(entries) == 1, 'Missing or duplicate marketplace entry')
    require((root/entries[0]['source']['path']).resolve() == plugin.resolve(), 'Marketplace source mismatch')
    for relative in ['uv.lock', 'examples/fastmcp-research/uv.lock',
                     'THIRD_PARTY_NOTICES.md', 'examples/fastmcp-research/SOURCE-LICENSE.txt']:
        require((root/relative).is_file(), f'Missing release material: {relative}')
    result = {'plugin_version': version, 'scrapling_version': upstream,
              'expected_tools': len(release['expected_mcp_tools']),
              'identity_version_paths': True, 'runtime_pins': True, 'skill_links': True,
              'license': True, 'marketplace_source': True,
              'schema_validation': 'passed' if schemas else 'skipped_offline'}
    if schemas:
        out = root/'artifacts/package'
        out.mkdir(parents=True, exist_ok=True)
        for name in ['plugin', 'mcp']:
            data = read_json(plugin/f'{name}.json')
            with urllib.request.urlopen(data['$schema'], timeout=30) as response:
                schema = json.load(response)
            jsonschema.validators.validator_for(schema)(schema).validate(data)
            (out/f'{name}.schema.json').write_text(json.dumps(schema, indent=2), encoding='utf-8')
            result[f'{name}_schema'] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Skip remote schemas, label result explicitly')
    parser.add_argument('--tag', help='Require tag to match release.json, e.g. v0.1.1')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = validate(root, schemas=not args.offline, tag=args.tag)
    out = root/'artifacts/package'
    out.mkdir(parents=True, exist_ok=True)
    (out/'checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
