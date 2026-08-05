# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-05 · 最新归档：`sessions/tg-rotate-2026-08-05-0915.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 截至 2026-08-05 初：上述两目录本地仍为 **未跟踪**（`git status` 可见 `??`），入库前勿当已交付
- [LESSON: dev-session-stage|主人说「stage1-6 干完先不发」时：可标 stage done + test 跑通，但 **禁止** 擅自 commit/push/海豚 publish/request-publish]
- 「运营系统·页面访问」表 `dws.dws_app_page_visit_d_d`（`dev-20260804-002`）；口径权威 http://54.255.236.159:8012/library/metric_page_visit_analysis
- 只账号；进入=来路空/`unknown`；只落分子分母；uid_cnt=BITMAP；跳转边表已删
- 代码目录：`ops_system/04.dws/dws_app_page_visit_d_d/`
- test `dt=2026-08-04` 已重跑（约 1.96 万行）；主人令先不发
- 待办：主人说可发再 commit/publish/request-publish
- 官方包来源：`/api/v1/extension/download/latest`；安装前必须做 **SHA256 校验**，与线上一致再装
- [LESSON: dc-platform|extension|security|官方 vsix 安装前必须 SHA256 校验通过，禁止跳过校验直接装]
- dc-platform 扩展双机升级：old-mac / new-mac **无 SSH 互通**，每台须在本机执行安装，不能远程代装
- 标准双机流程：先 `bash ~/.dc-platform/scripts/sync-memory-git.sh` 拉脚本，再 `bash ~/.dc-platform/scripts/install-dc-extension-latest.sh`
- 安装脚本已沉淀在 memory git：`memory/scripts/install-dc-extension-latest.sh`，会自动拉官方最新 vsix 并安装
- 装完须在 Cursor 执行 **`Developer: Reload Window`** 重载窗口，新功能（如审核流）才会生效
- 0.0.123 主要变更：恢复**发布审核流**——申请发布可指定审核人、撤回申请、审核人放弃审核、已发布 session 可发起确定修改

