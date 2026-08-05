# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-05 · 最新归档：`sessions/tg-rotate-2026-08-05-0915.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 截至 2026-08-05 初：上述两目录本地仍为 **未跟踪**（`git status` 可见 `??`），入库前勿当已交付
- [LESSON: dev-session-stage|主人说「stage1-6 干完先不发」时：可标 stage done + test 跑通，但 **禁止** 擅自 commit/push/海豚 publish/request-publish]
- 「运营系统·页面访问」PRD 落地拆成 **两个 dev session**，不是工作簿单独编号项：`dev-20260804-002`（`dws_app_page_visit_d`）+ `dev-20260804-003`（`dws_app_page_jump_d`）
- **visit 表**：页面日指标（PV/UV/进入/跳转/跳出率/停留/加载），账号维 + 设备维各一套
- **jump 表**：页面跳转分布（from→to），供来源/去向饼图
- 代码目录：`ops_system/04.dws/dws_app_page_visit_d/`、`ops_system/04.dws/dws_app_page_jump_d/`
- 口径已定：**进入** = 会话首页且来路非空；**刷新不算跳转**；空 uid/device 丢弃；按天聚合
- 2026-08-04 当晚进度：平台 Stage **1–6 已标 done**；test 上 DDL+ETL 已跑通（`dt=2026-08-03`）；bounce 异常已修
- 主人指令：**stage1-6 干完、先不发**——海豚 publish / request-publish / prod 均暂缓
- 待办链：**git commit/push** → test 验数/挂海豚 task → 主人说可发时再 request-publish
- 上游探数背景：知秋曾查 `dwd` 层 `app_page_view` 的 `page_load_time` 字段分布（8/3 单日），与 visit 表「加载」指标相关
- 官方包来源：`/api/v1/extension/download/latest`；安装前必须做 **SHA256 校验**，与线上一致再装
- [LESSON: dc-platform|extension|security|官方 vsix 安装前必须 SHA256 校验通过，禁止跳过校验直接装]
- dc-platform 扩展双机升级：old-mac / new-mac **无 SSH 互通**，每台须在本机执行安装，不能远程代装
- 标准双机流程：先 `bash ~/.dc-platform/scripts/sync-memory-git.sh` 拉脚本，再 `bash ~/.dc-platform/scripts/install-dc-extension-latest.sh`
- 安装脚本已沉淀在 memory git：`memory/scripts/install-dc-extension-latest.sh`，会自动拉官方最新 vsix 并安装
- 装完须在 Cursor 执行 **`Developer: Reload Window`** 重载窗口，新功能（如审核流）才会生效
- 0.0.123 主要变更：恢复**发布审核流**——申请发布可指定审核人、撤回申请、审核人放弃审核、已发布 session 可发起确定修改

