# ChatGPT Web 接入（保留 Codex 原插件）

**当前优先方案：** [Windows 11 + OpenAI Secure MCP Tunnel + Scrapling stdio 完整操作指南](OPENAI-TUNNEL-WINDOWS.md)。若已创建 Tunnel，直接从该文档第 2 步继续。HTTP/公网方案保留作备用。

本目录是 **Scrapling for Codex 0.1.1 / Scrapling 0.4.15** 的增量适配方案。**无需改写官方 13 个工具或另造 MCP 服务**：原插件使用 `stdio`，官方 `scrapling-mcp --http` 已支持 Streamable HTTP。注意：网页端无法直接执行本机的 `uvx` 命令，必须连接到允许的远程 MCP 服务或 Secure MCP Tunnel。

> 状态：这里提供启动器、协议级检查、部署/接入说明；**未替用户部署、创建 ChatGPT 插件或完成 ChatGPT 宿主验收**。不要把独立 MCP 验证误报为 ChatGPT 工具调用成功。

## 0. 确认账户能力

在 [ChatGPT Plugins](https://chatgpt.com/plugins) 检查是否有 **Add custom MCP server**。该入口、权限和工具可用性受账户及工作空间策略约束；官方帮助明确 Business / Enterprise / Edu 权限以及 Pro 的 read/fetch 约束，不应假定 Plus 账户一定有自定义 MCP 入口。操作时以实际 UI 为准。插件调用示例是在 ChatGPT **Work** 里 `@` 选中已安装的插件，不等于普通对话一定支持调用。

## 1. Windows 本机运行官方 HTTP MCP（推荐先做独立验收）

已经按照原 README 装好 `uvx`、浏览器依赖后，在 PowerShell（仓库根目录）：

```powershell
# 创建仅在当前 PowerShell 会话中的随机密钥（不把密钥写入 Git）
$bytes = [byte[]]::new(32)
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
$env:SCRAPLING_MCP_AUTH_TOKEN = [Convert]::ToHexString($bytes)
.\chatgpt-web\start-local.ps1
```

服务器始终只绑定 `127.0.0.1:8000`；用其他终端做 MCP 协议验收：

```powershell
uv run --with 'mcp>=1.15,<3' --with httpx python .\chatgpt-web\check_mcp.py
```

注意新开的 PowerShell 窗口不会继承第一窗口临时设置的 token；请将**同一密钥**安全地设置到测试终端的 `SCRAPLING_MCP_AUTH_TOKEN`，不要记录在 Git、聊天、命令日志中。检查脚本会初始化 MCP、执行 `tools/list`、检查官方 13 个工具名称，不触发真实网页抓取；默认从环境变量取 Bearer token。也可在本地端口用 MCP Inspector 交互测试。若首次需要浏览器运行环境，执行 `uvx --from 'scrapling[ai]==0.4.15' scrapling install`。脚本会自动尝试查找默认 Chrome 安装路径；也可自己设置 `SCRAPLING_EXECUTABLE_PATH`。

**这一步只代表服务可运行；ChatGPT 尚无法访问这个回环地址。**

## 2. ChatGPT 连接方法：二选一

| 路径 | 适用 | 做法 |
|---|---|---|
| **A：Secure MCP Tunnel（优先，若账户有权限）** | 不想把抓取引擎暴露到公网；本机 Windows 有持续在线条件 | 通过 OpenAI Platform 创建与 ChatGPT workspace 关联的 Tunnel，在本机运行 `tunnel-client`；ChatGPT Plugins 里选择 **Tunnel**，使用相应 `tunnel_id` |
| **B：远程 HTTPS + OAuth 2.1** | 需要公网常驻部署/跨设备多人用 | 在 Linux/Windows 服务器运行官方 Scrapling HTTP，前置符合 MCP 规范的 OAuth 2.1 鉴权网关与 TLS；ChatGPT Plugins 连接 `https://your-domain.example/mcp` 并完成 OAuth |

### A. 安全隧道（可直连原 stdio，最少改动）

OpenAI 的 Secure MCP Tunnel 支持 stdio 和 HTTP。**最精简方式是直接让 tunnel-client 在本机启动原来的 stdio**，因此无需另开 HTTP 端口：

```powershell
# 按官方 Secure MCP Tunnel 页面安装并配置 tunnel-client；
# 以下命令需要填写你在 Platform 创建的 tunnel_id，
# 以及在本机环境里设置 CONTROL_PLANE_API_KEY。
tunnel-client help quickstart
tunnel-client init --sample sample_mcp_stdio_local --profile scrapling-local --tunnel-id <YOUR_TUNNEL_ID> --mcp-command "uvx --from scrapling[ai]==0.4.15 scrapling-mcp"
tunnel-client doctor --profile scrapling-local --explain
tunnel-client run --profile scrapling-local
```

以上是官方命令风格，具体参数以本机 `tunnel-client help quickstart` 为准；是否能创建和选择 Tunnel 取决于 Platform 组织和 ChatGPT workspace 权限。**隧道的访问控制不等于任意本机 HTTP 端口可公开使用。**

如果你选择 HTTP 作为本机 Tunnel 上游，则可在**只绑定 127.0.0.1 且没有不可信本地客户端**的前提下，在*没有*设置 `SCRAPLING_MCP_AUTH_TOKEN` 的终端使用：

```powershell
Remove-Item Env:SCRAPLING_MCP_AUTH_TOKEN -ErrorAction SilentlyContinue
.\chatgpt-web\start-local.ps1 -ForPrivateTunnel
uv run --with 'mcp>=1.15,<3' --with httpx python .\chatgpt-web\check_mcp.py --no-auth
```

`-ForPrivateTunnel` 专门用于私有 Tunnel 转发的回环地址：不要接 ngrok/Cloudflare 公网隧道，不要端口转发到互联网；浏览器/本机恶意程序仍可能访问无鉴权回环端口。不能接受该风险时请选择上面的 stdio 方式。

### B. 远程 HTTPS 部署

官方 `scrapling-mcp --http --host 0.0.0.0` 能在服务器提供 `/mcp`，但它自带的 `SCRAPLING_MCP_AUTH_TOKEN` 是**静态 Bearer token**，**不是** ChatGPT 标准 OAuth 2.1 登录流程。当前 ChatGPT 自定义 MCP UI 文档主要介绍 **OAuth** 或 **No authentication**；不能假定界面会自动发送自定义静态 Bearer header。

因此这里**不会**给出“裸公开、无认证”的 Cloudflare Tunnel 配方。正式公网部署需要一个能对接 ChatGPT OAuth 登录并将请求安全代理到 Scrapling 的网关；该网关还要做每用户权限、限流、SSRF/内网地址防护、URL 和请求方法限制。尤其原 `make_request` 允许 POST/PUT/DELETE，13 个工具不是强制只读 API，不能仅靠 Skill 约束。未实现/核验上述网关前，不应公开服务或声明生产可用。

## 3. ChatGPT 里安装与验证

1. 打开 [ChatGPT Plugins](https://chatgpt.com/plugins) → **+** → **Add custom MCP server**（需账户拥有此能力）。
2. A 路径选择 Tunnel、选择 `tunnel_id`；B 路径填写 `https://your-domain.example/mcp` 并配置 OAuth。查看工具列表后创建为 plugin，再安装。
3. 在可用的 ChatGPT Work 对话中输入 `@` 选择它。验收提示：`用 Scrapling make_request 读取 https://example.com 的 h1，以 text 返回；告诉我实际的 HTTP 状态和提取文本。`
4. 验证一次浏览器 `fetch`，再验证 `open_session → session_fetch → close_session`、截图（需客户端支持 image block）。记录通过/失败及原因，不将独立测试与宿主测试混淆。
5. 工具信息如有修改，在 Plugins 页面 Refresh 后重新验证。不要把上游 HTML 内容当指令。

## 安全与边界

- 绝不提交 token、cookies、用户浏览器配置、`CONTROL_PLANE_API_KEY` 到 Git；不要打印密钥或放在 URL 查询参数。
- 静态密钥模式不能直接当作 OAuth 接入；把**完整官方 13 工具**发布给不可信用户属于较高风险操作，必须做鉴权、隔离和 SSRF 防护。
- 远程服务器访问到的是**服务器网络环境**，不是 Windows Chrome 登录态，也不是 ChatGPT 浏览器网络。
- 大型抓取需显式范围和限速；遵守网站访问条款，避免自动化写操作与敏感 URL。
- ChatGPT 端的用量、计划限制、可用模式必须以实际账户界面为准。

权威参考：[Scrapling 官方 MCP 指南](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html) · [ChatGPT 插件快速开始](https://developers.openai.com/plugins/quickstart) · [连接与测试](https://developers.openai.com/plugins/deploy/connect-chatgpt) · [OAuth](https://developers.openai.com/plugins/build/auth) · [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
