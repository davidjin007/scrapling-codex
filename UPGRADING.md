# 跟随 Scrapling 升级

以可审查的新版本跟进上游，不自动升级。插件 `0.1.1 → 0.1.2` 与 Scrapling `0.4.15 → 新版本` 各自记录。不要移动旧标签、修改已发布包或直接编辑 Codex 缓存。

## 1. 建立分支并审查上游

```powershell
git switch main
git pull --ff-only
git switch -c upgrade/scrapling-next
uv sync --locked
uv run --locked pytest -q
```

查看 [Scrapling Releases](https://github.com/D4Vinci/Scrapling/releases)、[PyPI](https://pypi.org/project/scrapling/)、目标标签源码/文档。检查 Python 要求、ai/rag extras、MCP 入口、工具名称/参数/返回结构、会话释放、批量限制、Markdown 清洗和浏览器安装方式。先在隔离环境探查，不改现有可用安装，不用 latest 文档替代同版参考。

## 2. 同步修改

| 位置 | 内容 |
|---|---|
| `release.json` | 插件版本、Scrapling 版本；工具集实际变化时才改 expected_mcp_tools |
| `plugins/scrapling-codex/plugin.json` 和 `.codex-plugin/plugin.json` | 相同的插件版本和展示信息 |
| `plugins/scrapling-codex/mcp.json` 和 `.mcp.json` | 相同的 `scrapling[ai]==目标版本` 固定值及启动配置 |
| 根 `pyproject.toml` | 维护项目版本与插件一致 |
| 示例 `pyproject.toml` | `scrapling[rag]==目标版本`；示例自身版本独立 |
| Skill、两份 README | 新参数、行为及固定安装命令 |
| `references/upstream/` 与 `references/SOURCES.md` | 替换为目标标签官方资料，保留许可证、来源和实际 ZIP SHA256 |
| `scripts/probe_mcp.py`、`scripts/verify_mcp.py` | 审核 MCP 版本与工具契约；工具集变化应显式改测试 |
| CHANGELOG、验收说明 | 版本映射、兼容性与实际通过/失败/未验证项 |

重新解析锁文件并检查 diff，不手改 lock 版本字符串：

```powershell
uv lock
uv lock --project examples/fastmcp-research --upgrade-package scrapling
uv sync --locked
uv sync --project examples/fastmcp-research --locked
rg '0\.4\.15|0\.1\.1' README.md CHANGELOG.md UPGRADING.md release.json pyproject.toml plugins scripts examples docs
```

搜索结果逐项判断；历史证据保留原版本，不能批量替换伪造新验收。机器校验覆盖运行配置，不能证明每句人类文档仍准确，必须人工复核 Skill 与参考资料的实际内容。

## 3. 回归并记录新证据

```powershell
uv run --locked pytest -q
uv run --locked python scripts/validate_package.py
uv run --project examples/fastmcp-research --locked pytest -q examples/fastmcp-research/tests
uvx --from 'scrapling[ai]==目标版本' scrapling install
uvx --from 'scrapling[ai]==目标版本' python scripts/verify_mcp.py --uvx (Get-Command uvx).Source
uv run --project examples/fastmcp-research --locked python examples/fastmcp-research/collect.py --out artifacts/upgrade-fastmcp
```

`verify_mcp.py` 从插件配置启动 MCP，外层 uvx 的版本不能代替内部版本证据。`probe_mcp.py` 只是辅助探查。抽查至少 3 页标题、代码块、正文和来源。`verify_scenario.py` 当前对照示例默认 output 的历史结构；新输出需在升级分支明确调整对照，不覆盖旧结果假装继续有效。

分别验证：初始化/实际工具 schema、静态/动态/stealth/截图、会话复用和释放、空结果/无效会话/超时、实际依赖清单。再在 Codex 对话内实际调用；独立 MCP 或 CI 成功均不替代宿主验收。为新版本新增证据目录，标明日期、版本和仍未通过的项目。

## 4. 安装与回退

记下 `codex plugin marketplace list` 的来源路径。根据当前 `codex plugin --help`、`codex plugin marketplace --help` 注册准备好的仓库根目录并重装/启用，核对 source、缓存版本及 MCP 固定值。保留其他插件；必要时重载 Codex。GitHub 发布本身不会切换原机 marketplace。

回退时用独立目录中的 `v0.1.1` 源码或 Release ZIP 恢复原 marketplace 来源并重新安装，核对 installed/enabled。Git checkout 旧源码不代表缓存也回退；不要删除全局配置来解决单个插件问题。

## 5. 发布新版本

完成审查、对应回归和 CHANGELOG，合并维护分支并确认主分支 CI。将占位符替换为实际清单值：

```powershell
uv run --locked python scripts/validate_package.py --tag v<新插件版本>
uv run --locked python scripts/package_release.py
git tag -a v<新插件版本> -m 'Scrapling for Codex <新插件版本>'
git push origin main
git push origin v<新插件版本>
```

创建对应 GitHub Release，上传两个 ZIP、两个 `.sha256` 和 `release-checks.json`。说明插件/上游版本、通过项及残余限制。未通过项如实标注并评估是否预发布，不能改结果；包从源码生成，不从旧缓存或手工改过的 ZIP 生成。
