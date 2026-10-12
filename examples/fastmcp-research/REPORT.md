# FastMCP 中文接入调研报告

采集日期：2026-10-12。范围：10个官方HTML文档页，清单见 `urls.json`。这份资料适合工具作坊后续开发 Python MCP 服务、编写客户端和设计 Codex plugin 封装。

## 对工具作坊的结论

FastMCP 可作为以后自研 Python MCP 的候选框架：它把函数、数据和提示模板暴露为 MCP 组件，并处理协议与连接生命周期。本次 Scrapling 插件已经有官方 MCP，无需再用 FastMCP 重写。该取舍是针对本作坊的判断。[官方介绍](https://gofastmcp.com/getting-started/welcome)

## 安装与版本

官方文档推荐 `uv add fastmcp`，也支持 `pip install fastmcp`，用 `fastmcp version` 查看实际安装版本。将来开发时应在具体工具项目建立独立环境，选定已发布版本并锁依赖；不要把 FastMCP 加入 Scrapling MCP 的运行环境。[安装](https://gofastmcp.com/getting-started/installation)

**版本限制：官网跟随 main，可能描述未稳定发布的功能。** 本次安装页展示的是 FastMCP 4.0.0 / MCP 2.0.0 的示例输出，不能据此认定本机已安装、PyPI当前稳定版就是该版本，或所有示例都兼容旧版本。本次只调研文档，没有安装或运行 FastMCP 服务。[main 说明](https://gofastmcp.com/getting-started/welcome)、[安装页示例](https://gofastmcp.com/getting-started/installation)

## 核心能力与设计用途

| 文档 | 核心能力 | 在作坊中的用途判断 |
|---|---|---|
| [Server](https://gofastmcp.com/servers/server) | FastMCP实例承载MCP组件和服务设置 | 为一个工具项目建立明确的服务边界 |
| [Tools](https://gofastmcp.com/servers/tools) | Python函数注册为可调用工具，类型信息用于schema与校验 | 查询、转换或操作入口；写操作权限应另行设计 |
| [Resources](https://gofastmcp.com/servers/resources) | URI资源和参数化资源模板 | 暴露可读取的配置、文档或结果 |
| [Prompts](https://gofastmcp.com/servers/prompts) | 可复用提示模板 | 为用户提供明确的交互入口和上下文 |
| [Client](https://gofastmcp.com/clients/client) | Python程序发现/调用工具并读取结果 | 在模型接入前先验证MCP协议与业务返回 |

客户端操作使用 `async with Client(...)` 管理连接生命周期；典型动作是 `list_tools()`、`call_tool()`。文档展示的 `result.data` 是Python值，`result.content` 可含文本、图像等MCP内容块。具体API仍应对照所锁版本验证。[Client](https://gofastmcp.com/clients/client)

## 本地运行与 Codex 接入

快速开始以 `FastMCP(...)` 创建服务，用 `@mcp.tool` 注册函数。`mcp.run()` 默认 stdio，建议放在 `if __name__ == "__main__":` 中；可用 `python my_server.py` 启动。[快速开始](https://gofastmcp.com/getting-started/quickstart)

也可用 `fastmcp run server.py`，CLI会导入服务对象；CLI不会执行脚本的 `__main__` 块。HTTP供远程连接，可显式选transport。以后制作本地 Codex plugin 时，将已验证的stdio启动命令放入MCP配置，再配置Skill与marketplace。这是本作坊的接入建议，不是此次已完成的新FastMCP服务。[运行](https://gofastmcp.com/deployment/running-server)

## 认证需求

认证机制适用于HTTP/SSE；stdio继承本地执行环境的安全边界。文档说 FastMCP 默认 `auth=None`，因此可访问的HTTP端点不会自动要求Bearer认证。远程部署需配置 AuthProvider 或明确负责的网关，并阻止绕开网关的直连；认证也不等于业务授权。首版作坊工具优先本机stdio，未来有远程需求再设计认证。[Authentication](https://gofastmcp.com/servers/auth/authentication)

## 采集质量与可复用性

- 首次和覆盖重跑均10/10 HTTP200，内容集和索引各10个唯一URL；失败日志为空。顺序并发1，请求开始间隔实测≥1秒。
- 正文选择 `#content`，标题取 `#page-title`。代码UI先规范化再交给官方Markdown转换，避免CSS变量被误判为隐藏高度。每页保留代码块；非激活标签页等隐藏内容可能被略去，不能把快照视作网站完整备份。
- 重新请求 installation、quickstart、running-server 原HTML，核验标题和9个安装/装饰器/启动代码片段，全部一致；证据见 `output/source-checks.json`。
- 逐页Markdown、JSONL、CSV和运行版本记录见 `output/`。脚本、URL白名单、uv.lock与运行说明都在本示例目录。重跑采集覆盖数据；本报告需根据新快照人工复核。

来源归属及转换说明见 `SOURCE-NOTICE.md`；上游许可证保留于 `SOURCE-LICENSE.txt`。
