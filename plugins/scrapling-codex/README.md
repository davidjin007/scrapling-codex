# Scrapling for Codex（本机非官方封装）

插件 **0.1.1** 使用官方 **Scrapling 0.4.15** MCP，服务标识 `scrapling_local`。提供网页抓取、动态内容、截图和 Python 爬虫开发参考；没有自研抓取服务器。`Read` 展示标签和默认 GET 不构成强制权限隔离。

## 安装

先安装 uv（Windows 可用 `winget install --id=astral-sh.uv -e`），再运行：

```powershell
uvx --version
uvx --from 'scrapling[ai]==0.4.15' scrapling install
```

HTTP 不需要浏览器；动态/stealth/截图需要浏览器组件。首次运行下载依赖并消耗磁盘空间。uvx 仅固定 Scrapling 顶级版本，实际依赖见工作坊验证记录；项目示例另有 uv.lock。

从 marketplace **根目录**执行：

```powershell
codex plugin marketplace add .
codex plugin add scrapling-codex@tool-workshop-local
codex plugin list
```

MCP 命令为 `uvx --from 'scrapling[ai]==0.4.15' scrapling-mcp`。安装后若宿主还沿用旧 PATH 或未刷新插件，重新连接/重启 Codex。保留其他插件；不要把源码当缓存修改。源码更新后按 CLI 提示刷新 marketplace 和重新安装，核对缓存版本。

## 13 个官方工具

- 请求：`make_request`、`bulk_get`。
- 浏览器：`fetch`、`bulk_fetch`、`stealthy_fetch`、`bulk_stealthy_fetch`。
- 会话：`open_session`、`open_request_session`、`session_fetch`、`session_make_request`、`list_sessions`、`close_session`。
- 图像：`screenshot`（需浏览器会话）。

`main_content_only` 只限制到 body，去导航要指定正文选择器。HTTP 超时为秒，浏览器为毫秒。批量工具没有并发/间隔参数；严格限速用顺序调用或 Python。一次性浏览器工具不接受 session_id。会话用完或失败后都要关闭。

安装后的最小验收提示：“使用 Scrapling MCP make_request 对 https://example.com 做 GET，提取 p（标题需 title + main_content_only=false），报告实际状态和内容，不使用其他抓取工具。”独立 Python 运行成功不能代替这项 Codex 验收。

## 结构与来源

`plugin.json`/`mcp.json` 是可移植格式；`.codex-plugin/plugin.json`/`.mcp.json` 是 Codex 兼容格式，两套版本、身份和参数保持一致。入口 Skill 位于 `skills/scrapling-web-crawl`，官方资料按需读取，包含原 BSD 许可证及来源记录。项目源码与官方资料不代表作者背书。

完整计划和验证记录见 marketplace 根目录 `docs/`；中等难度应用示例见 `examples/fastmcp-research/`。不使用付费代理、云部署或额外模型 API。

## 此 Windows 主机的浏览器适配

本机原有 Chromium 1243 出现 Windows SideBySide 启动错误。两套 MCP 配置使用官方环境变量 `SCRAPLING_EXECUTABLE_PATH` 指向 `C:/Program Files/Google/Chrome/Application/chrome.exe`。Scrapling 使用独立临时配置目录，不读取个人 Chrome 登录配置。其他机器需调整/移除该 env，或为调用传入 executable_path/real_chrome。启动命令和13个官方工具保持不变。MCP SDK 2.3.0 的部分异常只返回通用工具错误，详细原因见 MCP stderr 日志。
