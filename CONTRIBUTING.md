# 开发与验证

当前用于私有维护。新工作从分支开始；不修改其他工具作坊项目或已安装缓存。需要 Python 3.10+（CI 3.12）、uv 和 Git。

```powershell
uv sync --locked
uv run --locked pytest -q
uv run --locked python scripts/validate_package.py
uv run --locked python scripts/package_release.py
uv run --project examples/fastmcp-research --locked pytest -q examples/fastmcp-research/tests
```

根环境只装维护工具，示例独立锁定，MCP 由官方 uvx 单独启动。根测试验证版本失配、标签和打包边界；示例测试验证提取、导出、失败记录及磁盘错误。schema 检查访问 agent-plugins.org；`--offline` 只跳过远程 schema，不等于完整校验。

CI 在 Windows/Linux 做开发检查；`verify_mcp.py` 使用真实浏览器和受控本地站点，collect/verify_scenario 访问白名单网站，均显式现场执行。托管 CI 不代表 Windows Codex 宿主。

新行为先写复现测试，提交前运行 `git diff --check`，核对版本、上游许可和已知限制。记录实际结果，不以独立成功替代宿主成功。升级见 [UPGRADING.md](UPGRADING.md)。禁止提交凭据、账户配置、浏览器数据、原始模型日志、虚拟环境；精简历史证据的个人路径脱敏，原始日志保留本地。
