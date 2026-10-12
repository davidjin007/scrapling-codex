# Scrapling 0.1.1 GitHub Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 在用户 GitHub 创建完整、可升级的 Scrapling plugin 仓库与 v0.1.1 Release。

**Architecture:** 仓库位于工具作坊内独立目录，复制已验证的 0.1.1 交付树。`release.json` 记录版本契约，校验工具对照现有运行配置；CI 只做可重复的开发检查，真实网络和宿主验收保留分层证据。

**Tech Stack:** Python 3.10+、uv、pytest、jsonschema、Git、GitHub Actions、gh。

**Spec:** [repository-spec.md](../../repository-spec.md)

## Global Constraints

- 插件 0.1.1；Scrapling 0.4.15；MCP `scrapling_local`；marketplace `tool-workshop-local`。
- 不创建 AGENTS.md，不修改现有安装，不上传秘密，不自动升级。
- GitHub 初次建库和上传由用户明确授权；没有另行选择时默认私有。

## Review Focus

- 只改一份版本/依赖时，校验必须失败（Task 2 变异输入测试）。
- 新标签与清单失配时，发布检查必须失败（Task 2 tag 测试）。
- 隐藏配置/锁文件漏进 ZIP，或本地隐私文件误入 ZIP（Task 2 打包集成测试）。
- CI 在 Linux 与 Windows 的路径和锁文件行为（Task 3 真实 Actions 结果）。
- 历史证据与当前宿主能力混淆、第三方许可丢失（Task 3 人工核对）。

### Task 1: Repository snapshot and maintenance documentation

**Files:** README.md, CHANGELOG.md, UPGRADING.md, CONTRIBUTING.md, THIRD_PARTY_NOTICES.md, docs/architecture.md, docs/repository-spec.md, release.json, pyproject.toml, .gitignore.

**Interfaces:** Consumes original 0.1.1 tree. Produces standalone repository and `release.json` with `plugin_version`, `scrapling_version`, `expected_mcp_tools`.

- [ ] Copy curated source, verify original eight behavior tests pass. Expected: 8 passed.
- [ ] Add maintenance documentation; record private default and no root license grant decision.
- [ ] Scan paths/secrets and compare plugin bytes. Expected: 32 identical plugin files, no credentials.
- [ ] Commit snapshot and documentation.

### Task 2: Version validation and packaging

**Files:** scripts/release_config.py, scripts/validate_package.py, scripts/package_release.py, tests/test_release_tools.py, uv.lock.

**Interfaces:** Consumes Task 1 metadata. Produces `validate(root, schemas=True, tag=None)` and `package(root, output=None)`, two ZIPs, SHA256 and JSON inventory.

- [ ] Write tests exercising changed-version fixtures, changed dependency pins, invalid tags and archive contents/exclusions.
- [ ] Run `uv run pytest -q`. Expected: new behavior tests fail against current hardcoded scripts.
- [ ] Implement metadata loading, consistency validation and version-derived packaging.
- [ ] Run `uv run pytest -q` and `uv run python scripts/validate_package.py`; build ZIPs. Expected: tests green, schemas valid, CRC/hidden files valid.
- [ ] Commit tooling, tests and lock.

### Task 3: GitHub publication and review

**Files:** .github/workflows/ci.yml, .github/ISSUE_TEMPLATE/*, docs/github-publication.md.

**Interfaces:** Consumes Task 2 commands/artifacts. Produces main branch, v0.1.1 tag, release with ZIPs/checksums and actual CI evidence.

- [ ] Add Windows/Linux CI with locked maintenance and example environments, schema check, packaging and workflow artifact upload. No cron.
- [ ] Run whole suite, compare plugin snapshot, scan staged tree and request one fresh review. Expected: tests pass, no material unresolved findings.
- [ ] Create private repository unless user selects public, push main/tag and create v0.1.1 Release.
- [ ] Inspect remote refs, Release assets and actual Actions results. Expected: tag points to published commit; both CI jobs green.
- [ ] Record truthful results, commit publication record and verify final main CI. Link repository and Release in final response.
