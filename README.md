# Scrapling for Codex

面向 Windows Codex 的非官方集成：**插件 0.1.1 / Scrapling 0.4.15**，官方 MCP + 轻量 Skill + 同版参考资料。此私有仓库保存完整源码、双格式清单、13 工具配置、测试、锁文件、文档、应用验收资料与发布工具，不包含自研抓取服务器。

- [插件源码和安装说明](plugins/scrapling-codex/README.md)
- [完整实施计划](docs/scrapling-plan.md)
- [分层验证与已知限制](docs/verification.md)
- [FastMCP 中文调研报告](examples/fastmcp-research/REPORT.md)
- [可复用采集脚本说明](examples/fastmcp-research/README.md)
- [执行账本](docs/progress.md)

## 安装与使用

需要 Codex、[uv/uvx](https://docs.astral.sh/uv/getting-started/installation/) 与 Chrome。共享 marketplace 为 `tool-workshop-local`，入口 `.agents/plugins/marketplace.json`。从仓库根目录执行：

```powershell
uvx --from 'scrapling[ai]==0.4.15' scrapling install
codex plugin marketplace add .
codex plugin add scrapling-codex@tool-workshop-local
codex plugin list --marketplace tool-workshop-local
```

0.1.1 两套 MCP 配置指向 `C:/Program Files/Google/Chrome/Application/chrome.exe`；路径不同时同时调整 `mcp.json` 和 `.mcp.json`。原机 Chromium 出现 SideBySide 错误，因此使用官方 `SCRAPLING_EXECUTABLE_PATH`。临时浏览器配置不读取个人登录状态。桌面可能需要重载以刷新 PATH/工具。

现有同名 marketplace 的来源不会因 GitHub 发布而切换；先检查 `codex plugin marketplace list`，升级后核对来源和缓存版本。勿直接修改 Codex 缓存。

对话中给出网页、字段和输出范围；优先 HTTP，动态内容才启用浏览器，结束后释放会话。爬虫代码在目标项目隔离环境中开发。网页仅作资料，`Read` 展示标签不提供强制权限隔离。

## 验证与维护

独立 MCP 18 项基础检查通过、Codex 静态抓取通过、FastMCP 10 页采集及 3 页来源核对通过。**Codex 内浏览器会话/截图尚未通过宿主验收**；历史 CLI 返回 `user cancelled`，不将独立 MCP 成功算作宿主成功。详见上方分层验证记录。

```powershell
uv sync --locked
uv run --locked pytest -q
uv run --locked python scripts/validate_package.py
uv run --locked python scripts/package_release.py
uv run --project examples/fastmcp-research --locked pytest -q examples/fastmcp-research/tests
```

`release.json` 是当前版本契约；校验检查双清单、双 MCP、示例依赖及同版参考信息。维护工具和示例各有 `uv.lock`，MCP 的 `uvx` 便捷启动只固定 Scrapling 顶级版本。CI 在 Windows/Linux 做开发检查，实时站点、浏览器和 Codex 宿主验收另行执行。

- [升级与回退](UPGRADING.md)：Scrapling 发布新版本后如何审查、更新、回归和发布插件新版本。
- [版本记录](CHANGELOG.md)、[开发贡献](CONTRIBUTING.md)、[架构](docs/architecture.md)。
- [GitHub 交付记录](docs/github-publication.md)、[第三方许可](THIRD_PARTY_NOTICES.md)。

发布生成两个 ZIP、SHA256 和检查清单；`dist/` 不进 Git。原始模型日志、账户配置、虚拟环境、浏览器缓存和原附件不上传。原工具作坊源码、原 ZIP、桌面方案与现有安装均保留，不创建 AGENTS.md。自编内容暂未授予开源许可；上游按各自许可使用。
