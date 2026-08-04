# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-04 · 最新归档：`sessions/tg-rotate-2026-08-04-1714.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 官方包来源：`/api/v1/extension/download/latest`；安装前必须做 **SHA256 校验**，与线上一致再装
- [LESSON: dc-platform|extension|security|官方 vsix 安装前必须 SHA256 校验通过，禁止跳过校验直接装]
- dc-platform 扩展双机升级：old-mac / new-mac **无 SSH 互通**，每台须在本机执行安装，不能远程代装
- 标准双机流程：先 `bash ~/.dc-platform/scripts/sync-memory-git.sh` 拉脚本，再 `bash ~/.dc-platform/scripts/install-dc-extension-latest.sh`
- 安装脚本已沉淀在 memory git：`memory/scripts/install-dc-extension-latest.sh`，会自动拉官方最新 vsix 并安装
- 装完须在 Cursor 执行 **`Developer: Reload Window`** 重载窗口，新功能（如审核流）才会生效
- 0.0.123 主要变更：恢复**发布审核流**——申请发布可指定审核人、撤回申请、审核人放弃审核、已发布 session 可发起确定修改
- 0.0.122 的补数放开相关文案在 0.0.123 中保留
- 一台装完后应核对版本号（如 `dc-platform.dc-platform-0.0.123`），另一台跑完脚本后同样核对
- TG 群旁听：仅显式 @又初/@初儿/@youchu_ai_bot 等时才回复；裸提名字或 @ 别人只作背景，**不插嘴、不声明「我不回复」**
- 停留时长链路改审核人时，要扫**同链路所有 pending 的 request-publish**，不要只改当前 session；`dev-20260729-002` / `dev-20260711-002` / `dev-20260716-001` 三处曾一并从野花改到蓝猫（`hull367660@gmail.com`）。
- 他人已在 prod 发版后本地跟 session：**先 GET 服务端最新 state，再 merge PUT**；禁止整包覆盖，避免冲掉狂人写的 prod 信息。
- 2026-07 prod 结论：30 业务日全覆盖、分档符合设计、07-30 与上游对账无差；本地大改后**未 commit**，推 `origin/dev` 需主人明示。
- [LESSON: dev-session|session 被 admin 用 fix-metadata 摘表后，本地须同步改 task.yaml、文档口径，设备文件移 `_parked_*` 并为摘出范围新建独立 session，勿把已摘表推回 PUT `/full`]
- 已是 **approved** 的旧 session（如 `dev-20260711-001` DWD page_stay）不会随 pending 批量改审；若 prod 发版也要换人，需**单独处理**。
- `dev-20260729-002` 已收敛为**单目标表** `dws.dws_session_duration_user_d`；设备侧 `dws_session_duration_device_d` 从 outputs / `dolphin_owned_tasks` 摘掉，本地设备文件**移入** `ops_system/04.dws/_parked_session_duration_device_d/`，不要直接删。
- 设备 DWM 独立成新 session **`dev-20260731-001`**（`job_dwm_app_session_sid_device_d`）；用户侧 session 的 `task.yaml` / spec / README / playbook / design / memory 都要改成**单表口径**。
- 平台 session 同步用 **PUT `/full`**，并更新 `related_tables`、`title`、`target.note`；设备侧标 **`stage5.upstream_device=OUT_OF_SCOPE_SEPARATE_SESSION`**。

