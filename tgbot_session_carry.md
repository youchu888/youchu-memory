# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-21 · 最新归档：`sessions/tg-rotate-2026-09-21-2241.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 主人贴**已定稿**日报并说「上传云端」时：以粘贴正文为准，先落本地 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`，再跑上传脚本；**禁止**按记忆重写或润色正文
- [LESSON: daily-report,upload|主人贴定稿要求上传云端时，先原样落盘 reports/ 再跑 upload_work_report.py，禁止改写正文后再传]
- 上传云端是**独立触发**：只有主人明确说「上传云端」才执行；与写日报、推 TG 不是同一步
- 上传成功回执应带齐四件事：**日期**、**云端记录 ID**、**状态**（如 `inserted` / 覆盖）、**本地定稿路径**
- 同日同类型报告再次上传会走覆盖；首次新建常见状态为 `inserted`（本次 2026-09-19 → ID 100939）
- 上传脚本：`.cursor/scripts/upload_work_report.py --date YYYY-MM-DD`；未指定日期默认当日
- 周六也可写/上传日报；是否推 TG 与是否上传云端分开，本次仅为云端上传
- 日报「上传云端」场景：对话里确认「已上传 + 路径 + 记录 ID」即可，**不必再贴完整正文**
- 2026-09-19 日报实交付摘要：指标库同步包实体与角色种子改为**遇主键跳过写入**；撞车说明与索引已落盘；已催灌产切读授权
- 报障结论宜分层：**主机存活 / 记忆同步 / 远控通道** 分开说，避免把 ToDesk 问题说成「机器挂了」。
- 用户说「旧 Mac 挂了」时，先跑 `sync-memory-git` / 看 `host=old-mac|new-mac`，再查 TG bot、agent-bus poller 是否在跑；**远控连不上 ≠ 整机宕机**。
- 旧 Mac 仍是主控时，`youchu-memory` 同步成功、`ops-mirror/LATEST` 与双机 `hosts/*` 当日稿齐全，即可认定记忆已拉齐。
- ToDesk 断连常见是**客户端版本/远控问题**；bot、记忆同步、poller 正常则说明主机还活着。
- `sync` 流程可顺带触发 **ToDesk oneshot 升级**；是否完成看 `oneshot_upgrade_todesk.stamp`，未完成则下一轮 sync 再验。
- ToDesk 升级脚本走 `~/Downloads/ToDesk_Installer.app` 时，缺 **macOS 辅助功能权限**则 `cliclick`/自动化点不了「立即安装 / Install Now」，会卡在最后一键。
- 安装器按钮文案可能中英混用；点按逻辑需同时覆盖 **「立即安装」和 “Install Now”**，不能只写中文。
- ToDesk 官网 pkg **CDN 有反爬**，本机 `curl` 直链往往下不来，不能指望绕过 GUI 安装器。

