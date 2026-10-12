"""Behavior tests: missing cleaning, error handling or overwrite must fail."""
import json
from pathlib import Path

import pytest
from scrapling.engines.toolbelt.custom import Response

from collect import collect, extract_document, load_urls


def response(url, status=200, html=None):
    return Response(url=url,content=html or '''<html><head><title>Doc</title></head><body>
      <nav>SIDEBAR_NOISE</nav><h1 id="page-title">Install</h1><div id="content">
      <p>Use an isolated environment.</p><div class="code-block"><div style="--scroll-area-corner-height:0px"><pre><code language="python">print("ok")\n</code></pre></div></div>
      <button>COPY_NOISE</button><script>SECRET_NOISE</script><p aria-hidden="true">HIDDEN_NOISE</p>
      </div></body></html>''',status=status,reason='Test',cookies={},headers={},request_headers={})


def test_cleaning_preserves_ssr_code_and_discards_ui():
    doc=extract_document(response('https://docs.example/install'))
    assert doc['title']=='Install'
    assert 'print("ok")' in doc['markdown'] and '```' in doc['markdown']
    assert all(noise not in doc['markdown'] for noise in ['SIDEBAR_NOISE','COPY_NOISE','SECRET_NOISE','HIDDEN_NOISE'])


def test_missing_content_fails_instead_of_exporting_navigation():
    with pytest.raises(ValueError,match='content'):
        extract_document(response('https://docs.example/empty',html='<html><body><nav>Only navigation</nav></body></html>'))


def test_allowlist_deduplicates_and_rejects_non_http(tmp_path):
    path=tmp_path/'urls.json'
    path.write_text(json.dumps(['https://docs.example/a#x','https://docs.example/a','https://docs.example/b']))
    assert load_urls(path)==['https://docs.example/a','https://docs.example/b']
    path.write_text('["file:///C:/private"]')
    with pytest.raises(ValueError):
        load_urls(path)


def test_rerun_replaces_records_and_marks_failures_without_stale_markdown(tmp_path):
    urls=['https://docs.example/a','https://docs.example/b']
    collect(urls,tmp_path,fetch=lambda u,**kw:response(u),interval=0)
    first=json.loads((tmp_path/'pages.jsonl').read_text().splitlines()[1])
    collect(urls,tmp_path,fetch=lambda u,**kw:response(u,500 if u.endswith('/b') else 200),interval=0)
    rows=[json.loads(s) for s in (tmp_path/'pages.jsonl').read_text().splitlines()]
    assert len(rows)==2 and len({r['url'] for r in rows})==2
    assert rows[0]['status']=='ok' and rows[1]['status']=='error' and rows[1]['http_status']==500
    assert not (tmp_path/first['file']).exists()
    assert len((tmp_path/'errors.jsonl').read_text().splitlines())==1
    assert len((tmp_path/'index.csv').read_text().splitlines())==3


def test_request_starts_are_paced_and_redirects_disabled(tmp_path):
    ticks=[0.0]
    starts=[]
    def fetch(url,**kwargs):
        assert kwargs['follow_redirects'] is False
        starts.append(ticks[0])
        return response(url)
    def sleep(amount):
        ticks[0]+=amount
    collect(['https://docs.example/a','https://docs.example/b','https://docs.example/c'],tmp_path,fetch,interval=1,clock=lambda:ticks[0],sleep=sleep)
    assert starts==[0.0,1.0,2.0]


def test_transport_failure_is_not_success(tmp_path):
    def fail(url,**kw):
        raise TimeoutError('fixture deadline')
    collect(['https://docs.example/a'],tmp_path,fail,interval=0)
    row=json.loads((tmp_path/'errors.jsonl').read_text())
    assert row['status']=='error' and 'fixture deadline' in row['error']


def test_markdown_write_failure_is_exported_as_error(tmp_path,monkeypatch):
    write=Path.write_text
    def disk_full(path,*args,**kw):
        if path.suffix=='.md':
            raise OSError('fixture disk full')
        return write(path,*args,**kw)
    monkeypatch.setattr(Path,'write_text',disk_full)
    rows=collect(['https://docs.example/a'],tmp_path,lambda u,**kw:response(u),interval=0)
    assert rows[0]['status']=='error' and rows[0]['file'] is None and rows[0]['markdown'] is None
    assert 'fixture disk full' in rows[0]['error']
    assert len((tmp_path/'errors.jsonl').read_text().splitlines())==1
    assert json.loads((tmp_path/'run.json').read_text())['success']==0


def test_failed_cleanup_is_reported_without_aborting_error_export(tmp_path,monkeypatch):
    urls=['https://docs.example/a']
    first=collect(urls,tmp_path,lambda u,**kw:response(u),interval=0)
    write,unlink=Path.write_text,Path.unlink
    def fail_write(path,*args,**kw):
        if path.suffix=='.md': raise OSError('fixture write failure')
        return write(path,*args,**kw)
    def fail_cleanup(path,*args,**kw):
        if path.suffix=='.md': raise PermissionError('fixture locked stale file')
        return unlink(path,*args,**kw)
    monkeypatch.setattr(Path,'write_text',fail_write)
    monkeypatch.setattr(Path,'unlink',fail_cleanup)
    rows=collect(urls,tmp_path,lambda u,**kw:response(u),interval=0)
    assert rows[0]['status']=='error' and rows[0]['file'] is None
    assert 'fixture locked stale file' in rows[0]['error']
    assert (tmp_path/first[0]['file']).exists()
    assert json.loads((tmp_path/'errors.jsonl').read_text())['status']=='error'
