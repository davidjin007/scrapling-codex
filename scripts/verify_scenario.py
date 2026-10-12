"""Re-fetch three allowlisted source pages and compare observed code/prose."""
import json
from pathlib import Path
import time

from lxml import html
from scrapling.fetchers import FetcherSession

root=Path('examples/fastmcp-research/output')
rows=[json.loads(s) for s in (root/'pages.jsonl').read_text(encoding='utf-8').splitlines()]
assert len(rows)==10 and len({r['url'] for r in rows})==10
assert all(r['status']=='ok' and r['http_status']==200 and r['title'] and r['code_blocks']>0 for r in rows)
samples={
    '/getting-started/installation':['uv add fastmcp','pip install fastmcp','fastmcp version'],
    '/getting-started/quickstart':['from fastmcp import FastMCP','def greet(name: str) -> str:','@mcp.tool'],
    '/deployment/running-server':['mcp.run()','python my_server.py','fastmcp run server.py'],
}
checks=[]
with FetcherSession() as session:
    for row in rows:
        suffix=next((s for s in samples if row['url'].endswith(s)),None)
        if not suffix:
            continue
        page=session.get(row['url'],follow_redirects=False,retries=1,timeout=30)
        tree=html.fromstring(page.html_content)
        source=tree.cssselect('#content')[0].text_content()
        matches={snippet:snippet in source and snippet in row['markdown'] for snippet in samples[suffix]}
        title=tree.cssselect('#page-title')[0].text_content().strip()
        checks.append({'url':row['url'],'http_status':page.status,'title_matches':title==row['title'],
                       'snippets_match':matches,'extracted_code_blocks':row['code_blocks'],
                       'source_pre_elements':len(tree.cssselect('#content pre')),
                       'navigation_absent':'Search or jump to' not in row['markdown']})
        Path('artifacts/sources').mkdir(exist_ok=True)
        Path('artifacts/sources',suffix.rsplit('/',1)[-1]+'.html').write_text(page.html_content,encoding='utf-8')
        time.sleep(1)
run=json.loads((root/'run.json').read_text(encoding='utf-8'))
starts=[r['monotonic'] for r in run['requests']]
gaps=[b-a for a,b in zip(starts,starts[1:])]
result={'pages_ok':len(rows),'unique_urls':len({r['url'] for r in rows}),
        'minimum_request_start_gap':min(gaps),'concurrency':run['concurrency'],'spot_checks':checks}
(root/'source-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
assert min(gaps)>=1 and run['concurrency']<=2
assert all(c['http_status']==200 and c['title_matches'] and all(c['snippets_match'].values()) and c['navigation_absent'] for c in checks)
assert len(checks)==3
print(json.dumps(result,ensure_ascii=False,indent=2))
