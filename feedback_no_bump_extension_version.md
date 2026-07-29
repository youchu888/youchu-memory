# 死规矩 · 又初不改插件版本号 / 不自行发 vsix（主人 2026-07-29）

## 铁律

**禁止**自行改 `vscode-extension/package.json` 的 `version`、打 `dc-platform-*.vsix`、改 `dc-platform-server/extension/manifest.json`、调 `/api/v1/extension/publish` 发版。

插件发版属平台同学（野花 / 超管）。数据侧只报 bug、给 diff 或说明，**不升版、不发包**。

## 血案

又初为修 `advanceToStage` byCode，擅自 `0.0.121 → 0.0.122` 并 package；主人纠正后已回退版本产物。
