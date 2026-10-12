"""Controlled acceptance fixtures for the unmodified official MCP server."""
import argparse
import asyncio
import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HTML = '''<!doctype html><html><head><title>Fixture title</title></head><body>
<nav>Navigation noise</nav><main><h1>Fixture heading</h1><p id="state">Pending</p>
<pre><code class="language-python">print("scrapling")</code></pre></main>
<script>setTimeout(()=>{document.querySelector('#state').textContent='Dynamic ready';
document.cookie='browser_fixture=yes; path=/'},200)</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/slow':
            time.sleep(1)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        if self.path == '/set-cookie':
            self.send_header('Set-Cookie', 'fixture=yes; Path=/')
        self.end_headers()
        body = ('<html><body><main>' + self.headers.get('Cookie', 'NO_COOKIE') + '</main></body></html>') if self.path == '/cookie' else HTML
        try:
            self.wfile.write(body.encode())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def log_message(self, *args):
        pass


async def verify(args, url):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    events = []
    checks = []
    config = json.loads(Path('plugins/scrapling-codex/.mcp.json').read_text(encoding='utf-8'))['mcpServers']['scrapling_local']
    params = StdioServerParameters(command=args.uvx, args=config['args'], env=config.get('env'))
    with (out / 'baseline.stderr.log').open('w', encoding='utf-8') as err:
        async with stdio_client(params, errlog=err) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                tools = await client.list_tools()
                expected = {'make_request','bulk_get','fetch','bulk_fetch','stealthy_fetch','bulk_stealthy_fetch','open_session','open_request_session','close_session','list_sessions','screenshot','session_fetch','session_make_request'}
                checks.append(('13_tools', {t.name for t in tools.tools} == expected))

                async def call(name, **kw):
                    result = await client.call_tool(name, kw)
                    raw = result.model_dump(mode='json')
                    for block in raw['content']:
                        if block.get('type') == 'image':
                            data = base64.b64decode(block.pop('data'))
                            target = out / 'screenshot.png'
                            target.write_bytes(data)
                            block['saved_file'] = str(target)
                            block['bytes'] = len(data)
                    events.append({'tool':name,'arguments':kw,'result':raw})
                    print(name, 'ERROR' if result.is_error else 'OK', flush=True)
                    return result

                def has(result, text):
                    return not result.is_error and text in str(result.structured_content or result.model_dump())

                try:
                    r = await call('make_request',url=url,css_selector='h1',extraction_type='text')
                    checks.append(('static_selector',has(r,'Fixture heading')))
                    r = await call('make_request',url=url,css_selector='title',main_content_only=False,extraction_type='text')
                    checks.append(('title',has(r,'Fixture title')))
                    r = await call('make_request',url=url,css_selector='main',extraction_type='markdown')
                    checks.append(('markdown_code_and_no_nav',has(r,'```') and 'Navigation noise' not in str(r.structured_content)))
                    r = await call('make_request',url=url,css_selector='.not-present')
                    checks.append(('empty_selector',not r.is_error and not any(x.strip() for x in r.structured_content['content'])))
                    r = await call('session_fetch',url=url,session_id='not-present')
                    checks.append(('invalid_session',r.is_error))
                    r = await call('make_request',url=url+'/slow',timeout=0.1,retries=1)
                    checks.append(('http_timeout',r.is_error))
                    await call('open_request_session',session_id='http-fixture')
                    await call('session_make_request',url=url+'/set-cookie',session_id='http-fixture')
                    r = await call('session_make_request',url=url+'/cookie',session_id='http-fixture')
                    checks.append(('http_cookie_reuse',has(r,'fixture=yes')))
                    await call('close_session',session_id='http-fixture')
                    for mode, tool in [('dynamic','fetch'),('stealthy','stealthy_fetch')]:
                        r = await call(tool,url=url,css_selector='#state',wait=400,google_search=False)
                        checks.append((mode+'_one_shot_js',has(r,'Dynamic ready')))
                        await call('open_session',session_type=mode,session_id=mode+'-fixture')
                        r = await call('session_fetch',url=url,session_id=mode+'-fixture',css_selector='#state',wait=400,google_search=False)
                        checks.append((mode+'_session_js',has(r,'Dynamic ready')))
                        r = await call('session_fetch',url=url+'/cookie',session_id=mode+'-fixture',css_selector='main',extraction_type='text',google_search=False)
                        checks.append((mode+'_cookie_reuse',has(r,'browser_fixture=yes')))
                        if mode == 'dynamic':
                            r = await call('screenshot',url=url,session_id=mode+'-fixture',wait=400)
                            checks.append(('screenshot_image',not r.is_error and any(c.type == 'image' for c in r.content)))
                            r = await call('session_fetch',url=url+'/slow',session_id=mode+'-fixture',timeout=100,google_search=False)
                            checks.append(('browser_timeout',r.is_error))
                        await call('close_session',session_id=mode+'-fixture')
                    r = await call('open_session',session_type='dynamic',session_id='missing-fixture',executable_path=str((out/'does-not-exist.exe').resolve()))
                    checks.append(('missing_browser_error',r.is_error))
                finally:
                    r = await call('list_sessions')
                    # Session IDs are known even if opening/fetching fails midway.
                    for sid in ['http-fixture','dynamic-fixture','stealthy-fixture','missing-fixture']:
                        if sid in str(r.model_dump()):
                            await call('close_session',session_id=sid)
                    r = await call('list_sessions')
                    checks.append(('no_sessions_remaining',not any(s in str(r.model_dump()) for s in ['http-fixture','dynamic-fixture','stealthy-fixture','missing-fixture'])))
                    (out/'baseline-calls.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
                    (out/'baseline-checks.json').write_text(json.dumps(dict(checks),indent=2),encoding='utf-8')
    print(json.dumps(dict(checks),indent=2))
    assert all(passed for _,passed in checks), 'See baseline-checks.json'


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--uvx',required=True)
    parser.add_argument('--out',default='artifacts/mcp')
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        asyncio.run(verify(args,f'http://127.0.0.1:{server.server_port}'))
    finally:
        server.shutdown()
        server.server_close()
