# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-31 · 最新归档：`sessions/tg-rotate-2026-08-31-1108.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 「上传云端」与写日报、推 TG 是**独立指令**；主人单独说时才执行，写稿/推 TG 后**禁止**自动上传
- 口语「按这个上传云端」= 以**已定稿**日报为准，**不重新生成、不改写**正文
- 上传铁律：**原封不动**——禁止润色、补字、改格式后再传
- 定稿路径：`.cursor/work-log/reports/日报-YYYY-MM-DD.md`；未指定日期则用当日（Asia/Shanghai）
- 开工顺序：定位定稿 → 核对正文与上传脚本 → **原样上传** → 回报结果
- 标准脚本：`python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`
- 凭证读 `~/Downloads/工作报告/config.js`（apiToken，**不进 Git**）
- API：`https://ep.jsyyds.com/api/v1/report/submit`；成功 `code=0`；同日同类型再次上传会**覆盖**
- 成功回执应含四要素：**日期**、**云端记录 ID**、**状态**（如 `inserted` / 覆盖）、**本地定稿路径**，并明确「未改字」
- 周六等非工作日同样适用：有定稿即可上传，与 TG 推送日程无绑定关系
- 主人令「不要等狂人点头」：拍板类清库/改口径可先干完，再 bus 回执请他只读复核，不等事前确认
- G5 应用层门禁（service 校验）未落地；API 尚未切概念层读，需更多正式 published 后再切
- 未到打卡窗（如下班 19:00 前）API 会拒；禁止为验通知提前/强制打卡
- [LESSON: agent-bus协作|拍板/清库类任务主人说「不等点头」时：先执行落库，再 bus reply 对齐复核，禁止空等事前确认]
- [LESSON: onehr打卡|「打完卡通知」只加成功/失败后的 TG 私聊；禁止为验通知提前/强制打卡，须等到计划窗内自动跑完]
- 指标库 G2：`ratio` 不在 `default_aggregation` 白名单；derived 比率用分子/分母 FK，`default_aggregation` 留空
- 白名单仍是 `sum` / `count` / `bitmap_union_count` / `max` / `min`

