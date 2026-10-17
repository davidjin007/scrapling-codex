# OpenAI Secure MCP Tunnel — Windows 11 快速接入 Scrapling

**目标：ChatGPT Web → Secure MCP Tunnel → 本机 `uvx ... scrapling-mcp`（stdio）**。不部署公网 MCP，不使用 Cloudflare，不启动 `start-local.ps1`。原 Codex 插件和 `main` 分支不受影响。

**状态：操作说明（尚未完成目标 Windows 主机、ChatGPT 宿主实测）。** 当前已知上游 Scrapling 版本 0.4.15，插件 0.1.1，完整官方 MCP 共 13 tools。必须区分本地 `doctor`、Tunnel 在线和 ChatGPT 实际调用三层验收。

官方文档：
- [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
- [tunnel-client 最新 release](https://github.com/openai/tunnel-client/releases/latest)
- [OpenAI ChatGPT Plugins 接入步骤](https://developers.openai.com/plugins/deploy/connect-chatgpt)

## 1. 已创建的 Tunnel

使用 Platform → [Tunnels](https://platform.openai.com/settings/organization/tunnels) 中已有的 **Scraping OpenAI Tunnel**，点 ID 后面的复制图标获取完整 `tunnel_...` ID。不要新建第二个。确认它关联了**目标 ChatGPT workspace**，不只是 Platform organization。

## 2. 安装官方 Windows 完整 tunnel-client

从 [Platform Tunnels 页面](https://platform.openai.com/settings/organization/tunnels) 的 **Download tunnel-client** 或 [GitHub Releases](https://github.com/openai/tunnel-client/releases/latest) 下载**完整的** `tunnel-client-<version>-windows-amd64.zip`（Windows x64）或 `...-windows-arm64.zip`（Windows ARM64）。**不要选** `tunnel-client-runtime-...`（精简 runtime 未必包含首次 `init` 功能），更不需要 `runtime-cloudflared`。

在 PowerShell 中判断操作系统 CPU 架构：

```powershell
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
```

解压 ZIP 到私有目录（例如 `$HOME\Tools\tunnel-client`），找到其中的 `tunnel-client.exe`。将下列 PowerShell 变量设置为实际绝对路径，例如：

```powershell
$TunnelClient = "$HOME\Tools\tunnel-client\tunnel-client.exe"
& $TunnelClient --version
& $TunnelClient help quickstart
uvx --version
```

如果 ZIP 内有子目录，用 `Get-ChildItem "$HOME\Tools\tunnel-client" -Recurse -Filter tunnel-client.exe` 找实际路径。原 Windows Codex 已安装 `uvx` 的情况下，无需重复安装 Scrapling。

## 3. 创建受限 Runtime API Key（不需要充值）

在 [Platform Runtime API keys](https://platform.openai.com/settings/organization/api-keys) 里创建 **Restricted** Key，仅授权 **Tunnels: Read + Use**；如果 UI 不显示这些权限，先检查组织权限设置，不要改用 All 权限或 Admin key 作为代替。

不要把 Key 发给 AI / 放进 Git / 写入 profile / 加到用户级永久环境变量。**在本机 PowerShell 会话内**隐藏输入（随后只保存在该进程的环境变量和内存中，关闭 PowerShell 失效）：

```powershell
$secret = Read-Host "Paste restricted Tunnel Runtime API Key" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
  $env:CONTROL_PLANE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  $secret = $null
}
```

这把 Key 是给 `tunnel-client` 鉴权用；不是让用户通过 Responses API 调用模型。Tunnel 自身计费官方尚未明确承诺永久免费，保持 Billing 没有支付方式并检查 Usage。

## 4. 配置并运行 **stdio**（只需首次 init 一次）

把 ID 从 Platform 复制并在当前 PowerShell 中替换：

```powershell
$TunnelId = "tunnel_此处替换成平台复制的完整ID"

# 避免浏览器兼容问题：如本机安装路径存在，沿用原 Codex 的 Chrome 环境变量
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chrome) {
  $env:SCRAPLING_EXECUTABLE_PATH = $chrome
}

& $TunnelClient init --sample sample_mcp_stdio_local --profile scrapling-chatgpt --tunnel-id $TunnelId --mcp-command "uvx --from scrapling[ai]==0.4.15 scrapling-mcp"
& $TunnelClient doctor --profile scrapling-chatgpt --explain
& $TunnelClient run --profile scrapling-chatgpt
```

运行 `run` 的窗口保持打开，按 Ctrl+C 结束。**不要在同一个 Tunnel ID 上同时运行两个 stdio tunnel-client**；否则会话可能分到不同 MCP 子进程。二次启动时省略 `init`，只做 `doctor` + `run`；重开 PowerShell 后需要重新输入 Runtime Key。

如果 `doctor` 失败，暂停，不要盲目重复 `init`：按本地错误和官方排障文档分析。`doctor` 通过不代表服务端的 Read+Use 权限已正确配置；要看 `run` 日志和健康状态。默认健康面通常为 `http://127.0.0.1:8080/readyz` 和 `http://127.0.0.1:8080/ui`；如端口被占用或 profile 已覆盖，检查启动日志中的真实地址。

## 5. 在 ChatGPT 网页端建立私有 Plugin

1. 本地 `tunnel-client run` 保持在线后，打开 [ChatGPT Plugins](https://chatgpt.com/plugins) → Add → **Add custom MCP server**。
2. 填名称 **Scrapling (Local)**，描述 **Privately fetch and extract public webpages with Scrapling**。
3. Connection 选 **Tunnel**，选已存在的 **Scraping OpenAI Tunnel**，或粘贴 `tunnel_id`。如果列表不可见，检查 Workspace association 和 Tunnels Read+Use。
4. 创建并检查发现的工具列表，预计 13 项：`make_request`、`bulk_get`、`fetch`、`bulk_fetch`、`stealthy_fetch`、`bulk_stealthy_fetch`、`open_session`、`open_request_session`、`session_fetch`、`session_make_request`、`list_sessions`、`close_session`、`screenshot`。
5. 在支持的 ChatGPT 对话中选择该 Plugin，用以下安全、低成本测试提示词：`请只调用 Scrapling make_request，对 https://example.com 发 GET，选择器 h1，提取 text；报告实际状态码和内容，不使用其他抓取工具。`
6. 之后再针对实际需求测试 JS 动态抓取、打开/关闭会话和截图。独立验证通过 ≠ ChatGPT 插件宿主成功。

## 6. 常见故障

| 现象 | 优先排查 |
|---|---|
| `uvx` 找不到 | Windows PATH、重新打开 PowerShell，执行 `uvx --version` |
| `tunnel-client.exe` 找不到 | 解压路径；勿下载 runtime 精简版 |
| `doctor` 报 401/403 | Key 类型、所属 Platform 组织、Tunnels Read+Use |
| `doctor` 成功但 `run` 轮询 401/403 | 常见原因是 Runtime Key 缺 Tunnels Use |
| ChatGPT 找不到 Tunnel | Workspace association、用户权限 |
| 发现工具不是 13 个 | 检查实际启动的 Scrapling 版本和 stdio 日志 |
| 动态浏览器启动失败 | Chrome 路径、`SCRAPLING_EXECUTABLE_PATH`、浏览器依赖 |
| 创建插件时无法连接 | `run` 是否保持在线、健康状态及客户端日志 |

**边界：** 现有 13 个 Scrapling 工具中有可进行 POST/PUT/DELETE 的 `make_request`。工作流建议用 GET 不等于强制只读权限。不要上传身份凭证、个人 Chrome 浏览器配置或未获授权网站的访问资料。此 Tunnel 只用于私有连接，不可代替公开发布插件所需的公网 HTTPS MCP 服务。
