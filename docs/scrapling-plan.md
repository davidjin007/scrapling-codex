# Scrapling for Codex 实施与验收计划（执行版）

## 目标与约束

在工具作坊制作、安装本机 Windows Codex plugin：官方 Scrapling MCP + 轻量 Skill + 同版官方参考资料。支持抓取/字段/动态内容/截图和 Python 爬虫开发。用户已授权自动安装 uv、浏览器依赖、配置注册及测试，无需手动 PowerShell。**不创建任何 AGENTS.md**，原 ZIP 与桌面方案保留，附件视为审查资料。保留其他插件配置。不使用付费代理、云部署或额外模型 API。

## 源码与环境

- 源码 `plugins/scrapling-codex`，共享 marketplace `tool-workshop-local`（`.agents/plugins/marketplace.json`）。
- 插件版本0.1.1，Scrapling0.4.15，MCP标识 `scrapling_local`。保留可移植与 Codex 兼容元数据，统一版本与启动参数。
- Skill `scrapling-web-crawl` 分直接抓取、爬虫开发两条流程。导入固定版官方参考/示例/BSD许可证与来源校验记录，不照搬上游通用安装指令。
- 默认GET；写方法依用户明确授权；Read标签及Skill不宣称强制隔离。13个官方MCP工具，无自研服务器。正文选择器、批量工具无并发控制、会话释放、时间单位写明。
- 检测后必要时 `winget install --id=astral-sh.uv -e`、`uvx --version`、`uvx --from 'scrapling[ai]==0.4.15' scrapling install`。确认实际路径并预热依赖。
- 启动 `uvx --from 'scrapling[ai]==0.4.15' scrapling-mcp`。只固定顶级版本，记录实际依赖；示例独立环境和锁文件。

## 执行顺序和验证

1. 审查/导入附件，修订元数据、Skill与说明，验证JSON/schema、引用路径、版本和许可证。
2. 安装环境，独立MCP初始化并发现13工具。stdio保持协议，日志走stderr。
3. 静态标题/元素/Markdown；普通及stealth动态内容；截图图像；HTTP/浏览器会话复用与释放。
4. 空选择器、无效会话、超时和缺组件错误分别记录真实结果。缺组件以隔离浏览器路径模拟，不删除本机浏览器。
5. 用Codex支持的marketplace/plugin命令安装启用。实际Codex调用及结果留证；独立测试不得代替。若宿主须重启，记录断点，完成可继续项后重连验收。
6. 执行下面正式场景。最终审查、生成带隐藏文件的源码marketplace ZIP、安装说明与验证记录。

## 正式场景：FastMCP 中文接入调研资料包

FastMCP官方文档适合本作坊后续制作MCP/plugin：[官方介绍](https://gofastmcp.com/getting-started/welcome)。场景参考作者[文档采集用途](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html)。固定10页：welcome、installation、quickstart、servers/server、tools、resources、prompts、servers/auth/authentication、deployment/running-server、clients/client。

仅访问配置中URL白名单，不递归；并发≤2、同域请求开始间隔≥1秒。先通过已安装插件探查2页，检查正文/代码块，再用官方Python API制作可复用脚本。脚本接受URL清单、输出目录，独立环境固定0.4.15并锁依赖。

产物：逐页清洗Markdown、JSONL内容集、CSV索引（URL/标题/采集时间/状态）、中文报告（安装、能力、运行、认证、版本限制）、脚本、配置、说明和错误日志。官网文档跟随main，可能包含未发布功能；报告明确该限制，不能把文档全当成稳定版能力。

通过：10/10真实成功，标题/正文/代码有效，侧栏导航不成为主要内容；抽查≥3页对照原网页；重要结论链接具体页面；重跑覆盖不追加重复，失败单列不伪造。

## 完成条件

插件已安装启用 + Codex实际调用成功 + 正式场景通过 + 成果可复用。逐层标记通过/失败/未验证；外部网站或宿主阻塞明确记载，不把未通过算完成。最终交付源码、计划/README、marketplace ZIP、基础验证证据、FastMCP资料包。执行证据见 `docs/verification.md`，实施账本见 `docs/progress.md`。


## 当前实施状态（2026-10-12）

源码/Skill/参考资料、uv0.13.0与Scrapling0.4.15安装、marketplace注册及插件启用已完成。独立MCP18项通过；Codex实际GET读取FastMCP两页并验证正文代码；示例最终8个行为测试通过，10/10采集、重跑不重复、3页对照通过。独立复核发现的磁盘写入失败计数问题已修正并用回归测试验证。

本机浏览器使用官方SCRAPLING_EXECUTABLE_PATH连接已安装Chrome，解决原有Chromium的SideBySide错误；换机需调整或移除路径。MCP当前实际SDK为2.3.0，错误详情有时只在stderr可见。代码区先规范化以避开隐藏样式误判，隐藏标签页可能仍省略。

**保留断点：桌面重开后实际验证 open_session → session_fetch → screenshot → close_session → list_sessions。** CLI非交互会话创建/关闭被取消，不能把该项标成通过；当前对话尚未重载插件工具。无需再手动执行安装PowerShell。已交付的源码、资料包和独立浏览器验收证据均可复用。具体结果见verification.md。
