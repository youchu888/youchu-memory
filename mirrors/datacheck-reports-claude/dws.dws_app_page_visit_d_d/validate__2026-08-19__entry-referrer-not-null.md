# validate · dws_app_page_visit_d_d · dt=2026-08-19 · 进入=有来路

## 发版 / 补数

| 项 | 结果 |
|----|------|
| env | test |
| task | dws_app_page_visit_d_d (`22599391396992`) |
| version | 194 → **195** |
| complement PI | **69416** SUCCESS · COMPLEMENT_DATA · schedule 2026-08-20 05:20 |
| TI | **196644** SUCCESS |
| 分区 | `p20260819` / `dt='2026-08-19'` |
| 写入行数 | **22115**（日志 `execute update result: 22115`） |

## 口径确认（日志 SQL）

进入：`WHEN ref_pk IS NOT NULL THEN 1`（有来路）  
跳转：未改（`referrer=本页` 且目标≠本页，排除 unknown）

## playbook 对账（源表逐页）

本机 / MCP → test SR（`43.212.113.132:9030`）MySQL 握手失败（TCP 通、packet sequence / ERROR 2013），**未能在 Cursor 侧完成 entry_cnt 与 DWD 对账 SQL**。  
海豚侧已用新口径成功 OVERWRITE；数值对账待 SR 可达后补跑 playbook part_01/02 + 源表 reconcile。

## 判定

- 发版 + 补数：**PASS**
- 进入口径已上线到 test 线版：**PASS**（日志证据）
- 数值对账：**BLOCKED**（本机连不上 test SR）
