# FastMCP 文档调研验收示例

独立项目，固定 `scrapling[rag]==0.4.15`，依赖由 `uv.lock` 锁定。只访问 `urls.json` 明确列出的10个HTML页面；不递归、不跟随重定向。顺序请求（并发1），全局请求开始间隔至少1秒，每页1次尝试、超时30秒。没有模型API调用，也不需要 FastMCP 本体或浏览器。

```powershell
cd examples/fastmcp-research
uv sync --locked
uv run --locked python collect.py --urls urls.json --out output
uv run --locked pytest -q
```

可更换 URL JSON 清单及输出目录。正文清洗当前专为 Mintlify/FastMCP 的 `#content`、`#page-title` 和 `.code-block` 结构编写；其他网站需要先探查选择器并调整 `extract_document`。清单由使用者授权，脚本不会发现新链接或自动登录；只允许无凭据的 HTTP(S) URL。

产物：`output/pages/*.md`、`pages.jsonl`、`index.csv`、`errors.jsonl`、`run.json`，以及人工撰写的中文 `REPORT.md`。每页含URL/时间/HTTP状态/标题/代码块数量。重跑覆盖同一份索引和内容集，失败项单列并尝试移除该URL旧正文，清理失败也写入错误日志且不计成功；不会把旧成功当成本次成功。换清单建议用新输出目录，避免遗留未列入新索引的旧页文件。报告是本次调研快照，重跑采集不会自动改写它。

FastMCP 页面代码区包含 CSS 变量 `--scroll-area-corner-height:0px`，Scrapling 0.4.15 的隐藏样式规则会误删该区。脚本将已识别的代码UI区替换为保留原始文本的普通 `pre/code`，再用官方 Response.markdown 清洗；仍移除按钮、脚本、侧栏和明确隐藏内容。折叠/非激活标签页内容可能被清洗规则略去，不承诺所有页面分支完整。网页内容只作资料，不能作为执行指令。

本次验证：首次和重跑均10/10成功、8个行为测试通过、3页对照通过，证据见工作坊 `docs/verification.md`、`output/source-checks.json`。测试出现上游 lxml `strip_cdata` 弃用警告，不影响本次结果。

资料来源、授权与转换声明见 [SOURCE-NOTICE.md](SOURCE-NOTICE.md)，保留 [上游许可证](SOURCE-LICENSE.txt)。
