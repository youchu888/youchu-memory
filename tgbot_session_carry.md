# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-18 · 最新归档：`sessions/tg-rotate-2026-09-18-1211.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 报障结论宜分层：**主机存活 / 记忆同步 / 远控通道** 分开说，避免把 ToDesk 问题说成「机器挂了」。
- 用户说「旧 Mac 挂了」时，先跑 `sync-memory-git` / 看 `host=old-mac|new-mac`，再查 TG bot、agent-bus poller 是否在跑；**远控连不上 ≠ 整机宕机**。
- 旧 Mac 仍是主控时，`youchu-memory` 同步成功、`ops-mirror/LATEST` 与双机 `hosts/*` 当日稿齐全，即可认定记忆已拉齐。
- ToDesk 断连常见是**客户端版本/远控问题**；bot、记忆同步、poller 正常则说明主机还活着。
- `sync` 流程可顺带触发 **ToDesk oneshot 升级**；是否完成看 `oneshot_upgrade_todesk.stamp`，未完成则下一轮 sync 再验。
- ToDesk 升级脚本走 `~/Downloads/ToDesk_Installer.app` 时，缺 **macOS 辅助功能权限**则 `cliclick`/自动化点不了「立即安装 / Install Now」，会卡在最后一键。
- 安装器按钮文案可能中英混用；点按逻辑需同时覆盖 **「立即安装」和 “Install Now”**，不能只写中文。
- ToDesk 官网 pkg **CDN 有反爬**，本机 `curl` 直链往往下不来，不能指望绕过 GUI 安装器。
- 安装器已拉起时，可挂 **后台 watcher**：等人点完安装、pkg 落盘后，自动覆盖 `/Applications/ToDesk.app`、重启客户端并同步记忆。
- 旧 Mac 常见 **SSH 未开**（如 `192.168.1.12`），不能默认 SSH 远控可用。
- **没人在场**时的可行路径：① 用已在线的 **RustDesk** 连上再点安装或开辅助功能；② 用户从官网下 Mac 安装包，**私聊发给 TG bot**，由 bot 侧覆盖安装，无需碰键盘。
- 探测备援远控时要**真查进程/服务**：RustDesk 在线可用；AnyDesk 即使装了也可能**服务没起来**，别当默认备选。
- 大漏斗 prod **不在海豚挂 task**，是 **Spark 链路**；核查跑批状态应查 **SR 分区数据 + `update_time`**，不要先在海豚里找 workflow。
- 后续深挖方向：把 SF-81 的 `video_play` 与详情页 **交集逻辑拆开** 查根因，而非重跑全链路。
- 主表：`dws.dws_app_event_funnel_d_d`；口语「大漏斗今天正常跑了没」默认 **datacheck · prod · dt=T-1**。
- 跑通粗判：`dt` 分区有数、`update_time` 落在今早例行窗口（如 06:57）、行数/app 数与近一日环比量级正常。
- 2026-09-17 样例：**5,597 行 / 737 app**，`update_time=2026-09-18 06:57:46`；环比 09-16 注册 +1.2%、PV +2.3%、视频浏览 +2.4%，全站 video/novel/comic VIEW 非 0，new/old/-1 分区均有行 → **产线已跑通**。
- playbook 硬规则：**`video_play` 加总 ≤ 详情页 UV**；单 app 对照不过 ≠ 整表没跑，要分开报。

