# 架构与维护位置

| 路径 | 职责 |
|---|---|
| `.agents/plugins/marketplace.json` | marketplace 注册入口 |
| `plugins/scrapling-codex` | 插件发布单元，双格式清单/MCP、Skill、同版参考 |
| `examples/fastmcp-research` | 隔离采集环境、锁文件、测试、资料包 |
| `release.json` | 当前版本契约，失配时失败而不静默改配置 |
| `scripts` / `tests` | 校验、打包、独立 MCP/来源核对与维护测试 |
| `docs/evidence` | 精简历史验收证据 |
| `.github/workflows/ci.yml` | Windows/Linux 开发检查 |
| `dist` / `artifacts` | 生成发布包 / 本地过程输出，不进 Git |

Codex 通过官方 `uvx --from scrapling[ai]==0.4.15 scrapling-mcp` 调用 MCP；Skill 负责选择工具、输出范围、参考和爬虫开发。没有中间自研服务、付费模型或代理依赖。`Read` 不是权限隔离。

两个 uv.lock 分别锁维护环境和采集示例，MCP 仍只固定顶级版本。版本契约用于检查，运行时读实际插件配置，升级者必须同步修改和验收。

Git 工作副本位于工具作坊 `repositories/scrapling-codex`；原工具作坊保留原源码及已注册来源。仓库上传不切换安装。未来在 Git 副本维护，通过后再更新安装来源。Git 标签、源码目录、Codex 缓存是不同状态。

验证分为开发检查、真实独立 MCP/网站、Codex 宿主实际调用；三者不能替代。0.1.1 宿主会话/截图尚未通过，见 verification.md。
