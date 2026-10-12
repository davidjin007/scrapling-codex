# 安装与验收记录

执行日期：2026-10-12。源码版本0.1.1；Scrapling0.4.15；MCP标识 `scrapling_local`。本记录区分独立MCP、Codex调用和Python应用验收。

## 已安装状态

- `winget` 安装 uv0.13.0，`uvx --version` 实际返回版本。WinGet把Packages目录加入User PATH，当前已启动的桌面进程可能仍需重新打开以刷新PATH和插件工具列表。
- `uvx --from 'scrapling[ai]==0.4.15' scrapling install` 退出0，官方MCP运行环境已预热。实际 `mcp==2.3.0`；完整运行依赖见 `evidence/mcp-dependencies.json`。
- `codex plugin marketplace add .` 注册 `tool-workshop-local`；`codex plugin add scrapling-codex@tool-workshop-local` 安装到版本缓存0.1.1，`codex plugin list --marketplace tool-workshop-local` 显示 installed, enabled。保留其他插件。
- 两套MCP配置使用相同官方启动参数。此主机原有 Chromium1243 发生 Windows SideBySide 激活错误，故使用官方 `SCRAPLING_EXECUTABLE_PATH` 指向已安装Chrome。临时配置目录不读取个人浏览器配置；其他机器需调整路径。

## 验收分层

| 层级 | 实际结果 | 证据 |
|---|---|---|
| 包结构 | 通过：官方可移植JSON schema、双格式身份/版本、Skill引用、许可证、marketplace路径 | `evidence/package-checks.json` |
| MCP协议 | 通过：初始化Scrapling0.4.15，发现预期13工具，SDK能解析stdio，日志写stderr | `evidence/initialize.json`、`evidence/tools.json` |
| 静态/选择器 | 通过：受控HTML标题、h1、正文Markdown和代码；空选择器不伪造内容 | `evidence/baseline-checks.json` |
| 浏览器 | 独立MCP通过：普通及stealth执行延迟JS，截图返回PNG图像 | 同上、`evidence/screenshot.png` |
| 会话 | 独立MCP通过：HTTP及两类浏览器Cookie状态复用，结束/错误后会话清空 | `evidence/baseline-calls.json` |
| 异常 | 通过：无效会话、HTTP/浏览器超时、不存在可执行文件均返回is_error | 同上、`evidence/error-causes.txt` |
| Codex集成 | 通过范围：已安装插件实际make_request读取FastMCP两页，另验证代码块；list_sessions成功 | `evidence/codex-calls.json` |
| Codex会话/截图 | 尚未通过：CLI非交互调用open_session/close_session返回user cancelled，未执行session_fetch/screenshot；不算成功 | `evidence/codex-browser-attempt.json` |
| 正式应用 | 通过：首次和重跑10/10、10个唯一URL，8个行为测试通过，3页标题/9个片段对照一致 | `evidence/collector-*.log`、示例output/source-checks.json |

基础独立MCP共18项检查通过。受控本机HTTP fixture仅用于开发验收；正式场景只访问10页白名单，并发1，请求开始间隔实测≥1秒。截图验证不证明任何网站都可绕过限制。

## 已知边界和未验证项

- CodexCLI0.132.0不接受桌面默认模型gpt-6.1-sol，模型列表解析也遇到新枚举max；验收仅单次命令覆盖为账户返回可用的gpt-5.5，未改用户默认模型。CLI启动时其他插件的同步/清单警告保留在本地原始日志；未修改它们。
- CLI会话工具取消来自宿主调用流程，不能据此说浏览器本身失败，也不能把独立成功当成Codex截图成功。桌面重载后可用相同工具继续验收会话/截图；当前对话尚未动态加载新插件工具。
- MCP SDK2.3.0在客户端掩盖部分异常详情，只显示通用 `Error executing tool ...`；详细真实原因见stderr。本插件沿用官方服务器，未通过自研包装改写返回。
- FastMCP代码区的CSS变量被Scrapling隐藏规则误判。实际Codex用窄选择器 `#content` + `main_content_only=false` 验证代码存在；Python示例规范化代码区后仍使用官方清洗。非激活标签页可能被略去，已在报告标注。
- 单元测试出现上游lxml的strip_cdata弃用警告；没有失败。依赖顶级固定不等于完整锁定，示例有uv.lock，MCP运行版本另行记录。
- 未承诺强制只读隔离、付费代理、全站爬取、登录态复用、任意站点反检测成功或FastMCP新服务运行。正式场景无需这些能力。

## 可重复检查命令

刷新当前PowerShell的PATH后，从工作坊根目录执行：

```powershell
$env:PATH = [Environment]::GetEnvironmentVariable('PATH','User') + ';' + $env:PATH
codex plugin list --marketplace tool-workshop-local
uvx --from 'scrapling[ai]==0.4.15' --with jsonschema python scripts/validate_package.py
uvx --from 'scrapling[ai]==0.4.15' python scripts/verify_mcp.py --uvx (Get-Command uvx).Source
uv run --project examples/fastmcp-research --locked pytest -q examples/fastmcp-research/tests
uv run --project examples/fastmcp-research --locked python examples/fastmcp-research/collect.py
uv run --project examples/fastmcp-research --locked python scripts/verify_scenario.py
python scripts/package_release.py
```

原ZIP SHA-256 `397b0ba4c7e055dd7f6fd128cfc5fa9622cea246a092b8af4c3a0804ecdb077e`，官方同版参考ZIP SHA-256 `c6936ecad2ddf512ee942567bd0abb3a439fa2acc0b39fe95c5dcd80bd26ab88`。原ZIP与桌面方案均保留。最终发布包包含隐藏配置、源码、示例、锁文件、报告及精简验证证据，排除虚拟环境、浏览器缓存、原始模型日志和账户配置。发布包校验结果见dist目录。

最终独立复核及修正见 `review.md`。新增磁盘写入/清理失败回归测试先失败后通过，最终完整测试8/8；最后重新采集10/10并重做3页源内容对照。
