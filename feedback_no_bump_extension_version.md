# 死规矩 · 又初不改插件版本号 / 不自行发 vsix（2026-07-29 钦定 · 2026-08-04 再犯）

## 铁律

**禁止**自行改 `vscode-extension/package.json` 的 `version`、打 `dc-platform-*.vsix`、`cursor --install-extension` 装自打包、改 `dc-platform-server/extension/manifest.json`、调 `/api/v1/extension/publish` 发版。

插件发版属平台同学（野花 / 超管）。数据侧只报 bug、给 diff 或说明，**不升版、不发包、不自装自打 vsix**。

即使用户抱怨「申请发布不能选审核人」等插件缺陷：**只说明原因 + 可选代码 diff 给平台**；等官方 vsix 下发后再装。

## 血案

1. 2026-07-29：为修 `advanceToStage` byCode，擅自 `0.0.121 → 0.0.122` 并 package；纠正后回退。
2. **2026-08-04**：为修 request-publish 缺 `reviewer_username`，擅自 `→ 0.0.123`、本地 vsce、装进 Cursor；再次被纠正。已回退：工作区 restore、删自打 vsix、本机改回官方 `0.0.122`。

## 正确做法（申请发布 400）

- 根因：后端要 `reviewer_username`，官方 0.0.122 UI 只传 `note`
- 又初：用 API `request-publish` + `reviewer_username` 代提；或报给野花/超管改插件
- **禁止**：自己升版号 / 打 vsix / 装私包
