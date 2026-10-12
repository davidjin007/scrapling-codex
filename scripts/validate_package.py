"""Validate portable schemas, Codex compatibility, paths and pinned metadata."""
import json
from pathlib import Path
import re
import urllib.request

import jsonschema

root=Path('plugins/scrapling-codex')
out=Path('artifacts/package')
out.mkdir(parents=True,exist_ok=True)
results={}
for name in ['plugin','mcp']:
    data=json.loads((root/f'{name}.json').read_text(encoding='utf-8'))
    schema=json.loads(urllib.request.urlopen(data['$schema'],timeout=30).read())
    (out/f'{name}.schema.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
    jsonschema.validators.validator_for(schema)(schema).validate(data)
    results[f'{name}_schema']=True
portable=json.loads((root/'plugin.json').read_text(encoding='utf-8'))
compat=json.loads((root/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
for key in ['name','version','description','author','keywords']:
    assert portable[key]==compat[key],key
assert portable['version']=='0.1.1'
assert portable['extensions']['com.openai']['interface']==compat['interface']
assert len(compat['interface']['shortDescription'])<=30
assert all(len(p)<=128 for p in compat['interface']['defaultPrompt'])
a=json.loads((root/'mcp.json').read_text(encoding='utf-8'))['mcpServers']
b=json.loads((root/'.mcp.json').read_text(encoding='utf-8'))['mcpServers']
assert set(a)==set(b)=={'scrapling_local'}
assert {k:v for k,v in a['scrapling_local'].items() if k!='type'}==b['scrapling_local']
assert a['scrapling_local']['args']==['--from','scrapling[ai]==0.4.15','scrapling-mcp']
for key in ['skills','mcpServers']:
    assert (root/compat[key]).exists()
skill=root/'skills/scrapling-web-crawl/SKILL.md'
for link in re.findall(r'\]\(([^)]+)\)',skill.read_text(encoding='utf-8')):
    if not link.startswith(('http:','https:')):
        assert (skill.parent/link).exists(),link
assert (skill.parent/'references/upstream/LICENSE.txt').exists()
market=json.loads(Path('.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
assert market['name']=='tool-workshop-local'
assert (Path(market['plugins'][0]['source']['path'])/'.codex-plugin/plugin.json').exists()
results.update(identity_version_paths=True,skill_links=True,license=True,marketplace_source=True)
(out/'checks.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
