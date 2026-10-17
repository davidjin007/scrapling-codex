"""Offline regression for ChatGPT Web add-on, without MCP runtime."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[2]


def test_smoke_check_parses_and_has_13_expected_tools():
    code = (ROOT / "chatgpt-web/check_mcp.py").read_text(encoding="utf-8")
    tree = ast.parse(code)
    value = next(x.value for x in tree.body
                 if isinstance(x, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "EXPECTED_TOOLS" for t in x.targets))
    assert isinstance(value, ast.Set)
    assert len(value.elts) == 13


def test_http_launcher_is_loopback_only_and_pinned():
    code = (ROOT / "chatgpt-web/start-local.ps1").read_text(encoding="utf-8")
    assert "'127.0.0.1'" in code
    assert "scrapling[ai]==0.4.15" in code
    assert "SCRAPLING_MCP_AUTH_TOKEN" in code
    assert "--no-auth" in code


def test_existing_stdio_manifests_are_unchanged():
    import json
    for name in ("mcp.json", ".mcp.json"):
        config = json.loads((ROOT / "plugins/scrapling-codex" / name).read_text())
        assert config["mcpServers"]["scrapling_local"]["args"][-1] == "scrapling-mcp"
