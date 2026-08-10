# AGENTS.md

本仓是 `~/.agents/skills` 的 Git SSOT（shared harness 的 skills 唯一可写真源，consumer symlink 只读）。人类向说明见 `README.md` 与 `CONTRIBUTING.md`。

## Cloudflare 部署工作模式（用户指令 2026-08-10，适用于后续 Codex、对话和工作模式）

1. 网站改动完成并验证后，明确告诉用户已完成。
2. 明确说明是否触发了 Cloudflare Pages Build。
3. 默认使用本地构建 + Direct Upload（如 `wrangler pages deploy`），生成新的公开预览网址。Direct Upload 在本地构建、只上传成品，不消耗 Pages 每月 500 次 Build 配额；预览能力不受影响（每次部署有唯一 URL，指定 `--branch` 还有分支别名 URL）。
4. 若构建失败、无法上传或无法确认配额，如实说明，不伪称安全。
5. 只有用户明确要求正式 Git 集成部署时，才走该路径，并先提醒会消耗 Pages Build 配额。

边界说明：本仓关联的 `myk-skills-validation` 走 Workers Builds（按构建分钟计费，与 Pages 500 次/月是两套额度）；临时预览同样优先 Direct Upload，不为一次性预览浪费构建分钟。
