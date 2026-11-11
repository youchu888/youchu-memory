# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-12 · 最新归档：`sessions/tg-rotate-2026-11-12-0604.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 小时任务挂用户属性（知秋已定）**：只读 `dwm.dwm_user_attr_intraday_d_d`，`dt='D'`，按 `(app_id, uid)` LEFT JOIN；**禁止**小时格读 `dim.dim_user_snap`。
- `dim_user_snap` 单分区约十八亿行，小时任务每格全扫一次约多花 3 分钟+，是禁用的性能根因。
- 跨 owner 小时 SQL 仍可能旧口径：本名下无改动则 reply 写清「名下无小时 join snap」+ 点名旁观文件交给对口 owner，勿越权改他人稿。
- [LESSON: etl,hourly,user_attr|小时挂用户属性仅用 `dwm_user_attr_intraday_d_d` dt=D；禁小时读 `dim_user_snap`]
- 验「测试海豚能否登录」应双线：`/dolphinscheduler/ui/login` 可达（HTTP 200）+ MCP/API 鉴权成功且能列出项目（如运营系统、渠道系统）。
- 大号 TG prompt 文件：读开头指令与末尾「当前问题」，直接答问题，避免复述全文。
- 测试海豚入口形态：`http://<test-host>:12345/dolphinscheduler/ui/login`；默认 UI 账号为 `admin`，密码见本地 dolphin 配置或知识库，**蒸馏/lesson 不写明文密码**。
- 私聊要账号密码：从仓库内 test 海豚配置核对后回复；回复前宜先 UI/API 实测登录成功再交付。
- **小时任务挂用户属性（知秋已定）**：只读 `dwm.dwm_user_attr_intraday_d_d`，`dt='D'`，按 `(app_id, uid)` LEFT JOIN；**禁止**小时格读 `dim.dim_user_snap`。
- 旧说明「小时先 snap D-1 再叠日间表」作废；天任务仍用 `dim_user_snap` / `snap_dt=D`（或 D-1 按既有天任务口径）。
- 日间表可直接取：渠道、注册时刻、地区、设备、VIP、uid_code；编排上日间表应在同格先跑完再被小时消费。
- 收到 bus 派单：60 秒内 ACK → 实干 → reply 结案；ACK 若 `dropped: silent` 要查 `sent.json`/发送记录，不能当没发。
- 平台文档/asset 拉取失败（如 304/拿不到）时：不擅自改 canonical 文档，reply 注明未改原因。
- [LESSON: dolphin|test 登录验收=UI 200 + API 拉项目；账号密码只走配置源，不入公共记忆明文]
- [LESSON: agent-bus|ACK 若 silent drop 须核对发送记录；无责范围写清边界再 reply 结案]
- TG 超长 prompt（如 `prompt_*.md`）先读开头指令与末尾「当前问题」，按问题执行，勿复述全文。
- testcluster SSH 本机安装：`export GIT_SSH_BUNDLE_PASS="$(cat ~/.dc-platform/config/git-ssh-bundle.pass)"` 后跑 `bootstrap/testcluster-ssh/install-on-host.sh`（路径相对 memory 仓）。
- 登录默认是 `bigdata-dev`；要跑 Hadoop/集群侧命令用 `sudo -iu hadoop`，勿在 dev 用户下硬跑 hadoop 命令。

