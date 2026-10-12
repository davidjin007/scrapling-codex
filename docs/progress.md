# Execution ledger — plan: docs/scrapling-plan.md

## Constraints and rulings
- User approved the full plan and authorized uv, browser dependencies and Codex plugin installation. Do not create AGENTS.md or change unrelated plugin settings.
- Ruling: work directly in the explicitly requested empty workshop folder. It is not a Git repository, so worktree/commit helper scripts do not apply; preserve this durable ledger instead. Cost: no Git history until the user chooses repository setup.
- Pre-flight: plugin identity/server ID is shared by portable MCP, compatibility MCP, Skill, marketplace and verification. Keep `scrapling-codex`, `scrapling_local`, `0.1.1`, and upstream `0.4.15` consistent.

## Tasks
- [x] Inspect existing state and import original ZIP without changing it.
- [x] Import v0.4.15 official references/examples/license with SHA-256 verification.
- [x] Install uv 0.13.0 through winget (installer reported success).
- [x] Revise plugin, Skill and documentation.
- [x] Verify runtime and all MCP baseline scenarios.
- [x] Register/install plugin and verify actual Codex invocation.
- [x] Build and verify the reusable FastMCP research example.
- [x] Review, package and document final evidence.

## Source evidence
- Original ZIP SHA-256: `397b0ba4c7e055dd7f6fd128cfc5fa9622cea246a092b8af4c3a0804ecdb077e`.
- Official Skill ZIP SHA-256: `c6936ecad2ddf512ee942567bd0abb3a439fa2acc0b39fe95c5dcd80bd26ab88`.
- Winget installed uv into its per-user Packages directory and added that directory to User PATH; it did not create the initially expected WinGet/Links file. Use the verified actual executable while the current host still has its old environment.

- Ruling: use official SCRAPLING_EXECUTABLE_PATH for the installed Chrome in both Windows MCP configs — pre-existing Chromium 1243 fails Windows SideBySide activation, while Chrome launch was verified. Temporary profiles only. Cost: a machine without Chrome at this path must change/remove this override.
- Actual Codex CLI probe used per-run model gpt-5.5 (available in its account model response), since CLI 0.132.0 rejects the desktop default gpt-6.1-sol; user defaults were preserved. Two installed-plugin make_request calls succeeded (artifacts/codex-probe-retry.jsonl).

- Completed: schemas/paths/version checks passed; independent MCP 18/18 checks passed; collector 6 tests RED→GREEN, first run and rerun 10/10, source comparison 3/3. Evidence curated under docs/evidence.
- Codex CLI browser-session checks remain unverified: noninteractive approval returned user cancelled even with per-invocation tool policy. Static make_request through installed plugin succeeded; do not label the CLI session attempt as passed.
- Ruling: normalize only the identified Mintlify code-block wrappers before official sanitization — CSS custom variable is mistaken for height:0 and loses valid code. Cost: inactive/hidden tab branches may still be omitted; documented, not a full-site backup.

- Final: fixed Markdown write failure counted as success — test_markdown_write_failure_is_exported_as_error and test_failed_cleanup_is_reported_without_aborting_error_export RED→GREEN; full suite 8/8. No deferred minor findings.
- Final: Ruling: live Codex browser/session acceptance remains pending — user-approved plan permits a host reload boundary; actual installed-plugin GET is proven but CLI session/screenshot is not. Cost: desktop session and screenshot calls must still be checked after reconnect.
- Final: Ruling: no full historical snapshot of unrelated configuration — install used supported additive plugin commands and current known plugins/default model remain present, but full before/after identity cannot be asserted. Cost: no independent proof for every unrelated setting.

- Final verification: full suite 8/8, final collection10/10, source checks3/3; source/cache32 files identical; originalZIP hash unchanged; no project AGENTS.md; default model and known plugins remain enabled.
- Remaining host checkpoint: reopen desktop Codex, then actual browser session/screenshot acceptance. Keep this open; no completion claim for that item.
