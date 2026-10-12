# GitHub 0.1.1 交付记录

日期 2026-10-12，所有者 davidjin007，仓库 scrapling-codex，用户明确选择私有。目标 main / v0.1.1。

筛选复制已验收源码，保留插件、示例、锁文件、报告、精简证据。仓库证据的个人绝对路径替换为 `<LOCAL_USER_HOME>`，不改结果；插件目录不脱敏，以保持 32 文件字节一致。原始日志留在原工作坊未上传。Git 使用 noreply 邮箱。

新增维护文档/工具；自编内容暂未授予开源许可，上游 BSD/Apache 原文保留。发布和 CI 实际结果执行后补记；本次开发检查不补齐历史宿主会话/截图限制。

## 发布前验证

- 原示例测试 8/8，通过；已知上游 lxml 弃用警告保留。
- 新维护测试 7/7，先观察旧脚本失败，再验证修订后通过。
- 远程 portable plugin/MCP JSON schema 与 v0.1.1 标签一致性通过。
- 两个 ZIP CRC/隐藏文件检查通过，插件目录 32 文件与原源码字节一致。
- 定向敏感信息扫描未发现实际令牌、私钥、个人邮箱或个人 home 路径；代理凭据匹配均为上游文档 user/pass 占位示例。
- 新增变更的 staged diff --check 通过。整个导入范围仍有上游/历史资料空白问题，不宣称全范围 whitespace 检查通过。
- 独立只读审查 eb15d95..f075302 未发现实质问题；审查未重跑网站、浏览器或 CI。

## 本次维护决策

- 用户已授权创建/上传，直接在本对话执行；没有再询问计划确认。
- 独立仓库副本而非为无 Git 的共享工具作坊建 worktree；代价是原安装来源需在未来升级时显式切换。
- 私有仓库由用户确认；自编内容暂不新授开源许可，未来公开需另行选择。
- 保留原 CRLF 字节；历史资料 whitespace 不批量修正，以保留来源。
- 审查不重新判断原插件/上游内部行为；独立历史证据照实保留，若后续升级会重新验证。
- 审查不补齐 Codex 宿主会话/截图；用户不能据此认为该层已通过。
- 网站实时行为与法律许可充分性不由代码审查保证；保留本次快照与上游许可，更新/公开时重新核对。

## GitHub 实际 CI

仓库：[davidjin007/scrapling-codex](https://github.com/davidjin007/scrapling-codex)，visibility=private，默认分支 main。

[首次实际 Actions 运行](https://github.com/davidjin007/scrapling-codex/actions/runs/38282666331)：提交 `028c694fd6af65b5713e2307430a017884a4c367`，Windows/Linux 两个 job 均 success，包含根测试 7 项、示例 8 项、在线 schema 校验与打包。完整 job/step 状态在 `evidence/github-ci-initial.json`。这不是浏览器或 Codex 宿主验收。

插件 32 文件 SHA256 清单在 `evidence/plugin-source-snapshot.json`。发布入口：[v0.1.1 Release](https://github.com/davidjin007/scrapling-codex/releases/tag/v0.1.1)，两个 ZIP、各自 SHA256 和 release-checks.json；实际发布与标签检查以该 Release 及对应 Actions 为准。
