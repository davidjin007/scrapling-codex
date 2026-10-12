"""Sequential, explicitly allowlisted HTML collection using official Scrapling."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time
from urllib.parse import urldefrag, urlsplit

from lxml import html
from scrapling.engines.toolbelt.custom import Response
from scrapling.fetchers import FetcherSession


def load_urls(path):
    values = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(values, list) or not values:
        raise ValueError('URL list must be a nonempty JSON array')
    urls = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError('Every URL must be a string')
        url = urldefrag(value.strip())[0]
        parts = urlsplit(url)
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
            raise ValueError(f'Expected HTTP(S) URL without credentials: {url}')
        if url not in urls:
            urls.append(url)
    return urls


def extract_document(page):
    root = html.fromstring(page.html_content)
    matches = root.cssselect('#content')
    if len(matches) != 1:
        raise ValueError('Expected exactly one #content document body')
    title_nodes = root.cssselect('#page-title, h1')
    if not title_nodes:
        title_nodes = root.cssselect('title')
    title = title_nodes[0].text_content().strip() if title_nodes else ''
    if not title:
        raise ValueError('Missing document title')
    content = matches[0]
    # Mintlify's --scroll-area-corner-height:0px matches Scrapling 0.4.15's
    # hidden-style heuristic. Replace ONLY the known code UI wrapper with
    # canonical pre/code before official sanitization; do not disable it.
    for wrapper in list(content.cssselect('.code-block')):
        pres = wrapper.cssselect('pre')
        if not pres:
            continue
        replacement = html.Element('div')
        for pre in pres:
            new_pre = html.Element('pre')
            code = html.Element('code')
            language = pre.get('language') or (pre.cssselect('code')[0].get('language') if pre.cssselect('code') else None)
            if language:
                code.set('class', f'language-{language}')
            code.text = pre.text_content()
            new_pre.append(code)
            replacement.append(new_pre)
        replacement.tail = wrapper.tail
        wrapper.getparent().replace(wrapper, replacement)
    for node in list(content.cssselect('script, style, noscript, template, nav, aside, button, svg, img, [aria-hidden="true"], a[aria-label="Navigate to header"]')):
        node.drop_tree()
    content.make_links_absolute(page.url)
    cleaned = Response(url=page.url, content=html.tostring(content, encoding='unicode'), status=page.status,
                       reason='Extracted', cookies={}, headers={}, request_headers={})
    markdown = cleaned.markdown().strip()
    if len(markdown) < 20:
        raise ValueError('Empty or insufficient document content')
    return {'title':title, 'markdown':markdown, 'code_blocks':markdown.count('```') // 2}


def collect(urls, output, fetch, interval=1.0, clock=None, sleep=None):
    clock = clock or time.monotonic
    sleep = sleep or time.sleep
    output = Path(output)
    (output/'pages').mkdir(parents=True, exist_ok=True)
    records = []
    starts = []
    last_start = None
    for url in dict.fromkeys(urls):
        if last_start is not None:
            sleep(max(0.0, interval-(clock()-last_start)))
        last_start = clock()
        starts.append({'url':url,'monotonic':last_start})
        name = hashlib.sha256(url.encode()).hexdigest()[:16]+'.md'
        target = output/'pages'/name
        row = {'url':url,'final_url':None,'title':None,'collected_at':datetime.now(timezone.utc).isoformat(),
               'status':'error','http_status':None,'file':None,'markdown':None,'code_blocks':0,'error':None}
        try:
            page = fetch(url, timeout=30, retries=1, follow_redirects=False)
            row['http_status'] = page.status
            row['final_url'] = page.url
            if page.status != 200:
                raise ValueError(f'HTTP {page.status}; redirects are not followed outside the allowlist')
            doc = extract_document(page)
            target.write_text(f"# {doc['title']}\n\nSource: {url}\nCollected: {row['collected_at']}\nModified copy: cleaned HTML and normalized code wrappers; see ../../SOURCE-NOTICE.md and ../../SOURCE-LICENSE.txt.\n\n{doc['markdown']}\n",encoding='utf-8')
            row.update(doc)
            row.update(status='ok',file=f'pages/{name}')
        except Exception as exc:
            row.update(status='error',file=None,markdown=None,code_blocks=0,error=f'{type(exc).__name__}: {exc}')
            # Remove only this collector's deterministically owned page file.
            try:
                target.unlink(missing_ok=True)
            except OSError as cleanup_exc:
                row['error'] += f'; stale file cleanup failed: {type(cleanup_exc).__name__}: {cleanup_exc}'
        records.append(row)
    def jsonl(path, rows):
        path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    jsonl(output/'pages.jsonl', records)
    jsonl(output/'errors.jsonl',[r for r in records if r['status']=='error'])
    with (output/'index.csv').open('w',encoding='utf-8-sig',newline='') as file:
        fields=['url','final_url','title','collected_at','status','http_status','file','code_blocks','error']
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)
    versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    (output/'run.json').write_text(json.dumps({'requests':starts,'concurrency':1,'interval_seconds':interval,
        'success':sum(r['status']=='ok' for r in records),'total':len(records),'versions':versions},indent=2),encoding='utf-8')
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--urls',type=Path,default=Path(__file__).with_name('urls.json'))
    parser.add_argument('--out',type=Path,default=Path(__file__).with_name('output'))
    parser.add_argument('--interval',type=float,default=1.0)
    args=parser.parse_args()
    if args.interval < 1:
        parser.error('--interval must be at least 1 second')
    urls=load_urls(args.urls)
    with FetcherSession() as session:
        records=collect(urls,args.out,session.get,interval=args.interval)
    count=sum(r['status']=='ok' for r in records)
    print(f'{count}/{len(records)} pages succeeded; output: {args.out.resolve()}')
    raise SystemExit(0 if count==len(records) else 1)


if __name__ == '__main__':
    main()
