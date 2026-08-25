# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-25 · 最新归档：`sessions/tg-rotate-2026-08-25-2018.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 主人说「重新推送昨天日报」时：先定位 `reports/日报-YYYY-MM-DD.md` 定稿，再跑 `post_daily_report_to_dm.py --date YYYY-MM-DD`，不要拿旧缓存或半成品推。
- agent-bus 派单：60 秒内先 `ack`，干完再 `reply` 结案；同一 Cursor 主会话处理，勿 spawn 新 Agent。
- 设计可视化审稿（如 metric_library v0.3 id=66）：对照源稿 id=67 逐条核对章节门禁（G1–G7、U1–U10、Phase 0–4+2.5），缺啥补啥，不要只回「主体达标」。
- 可视化 HTML 铁律：纯 HTML/SVG 手工 ER，禁 mermaid CDN；v0.3 新增字段用 `hi` 黄底高亮；浅色卡片底 `#f4f5f7`，TOC 可快跳。
- 再审/补稿前**必须先对平台现网正文**（本地稿 ≠ 现网）；若现网已是较新的「组合约束」版，应以现网为底再 merge 缺失段落，而不是盲目重传本地旧补丁。
- TG 日报私聊推送默认**只发正文**：去掉「📋 又初 · 日报 …（定稿自动推送）」类标题头；改 `post_daily_report_to_dm.py` 后要让主人在 TG 目视确认格式。
- 推送脚本/日报相关改动要同步进 `youchu-memory`（memory git），避免另一台机或定时任务仍用带头版本。
- 审稿常见缺口清单（本轮）：§1 九数基线、§12.5 事件字典自增长、§13.3 四机制、§15 三表导出、§16 `metric_standard` 映射；ER 锚点错位需单独修。
- 「组合约束」类增补（C1–C4：dim_uses 成对、G7-b 三角等式、published 多件套等）与上述核心缺口**都要保留**，不能后补一版把前一轮补丁盖掉。
- 覆盖上传开发平台可视化后：reply 里写清改了哪些 §、平台路径/id，并提示可按审稿意见转交下一审核人（如知秋）。
- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 指标库 ER 图必须以用户指定的 **`spec_v0.3_20260824.md`** 为准；v0.3 扩层表名用正式稿 **`entity_dict` / `event_ext` / `role_dict`**，不用旧的 `domain_entity` 等临时名。
- 用户问「画好了吗 / 推文档库」时，标准链路：**核对 spec 版本 → 对齐表名重画 → 推文档库 → 报 slug/链接 → 附本地镜像路径**；未明确要求不要擅自 commit/push。
- 「正常了可以干活吗」类探活：短答可干活 + 点明根因（会话连不上）+ 列出可续两项（ER 图 / 其它数据活），让用户直接指定下一步。
- [LESSON: cursor-session,metric-library,er-diagram|会话 resume 失败续做时，先查本地稿并对齐最新 spec 表名再推文档库，勿用旧临时名或旧版 spec 交差]
- Cursor 会话 `resume` 被丢弃时，故障在 IDE 连接/会话恢复，不等于业务逻辑或数据本身出错；恢复后先说明原因再续做。
- 会话中断后续做，先查本地是否已有半成品（如 `docs/metric_library_er_diagram*.html/.md`），再对照用户最新 spec 决定补全还是重画，避免盲重做或交旧稿。
- 配色约定：蓝 = v0.2 指标核（concept / label / implementation / candidate）；黄 = v0.3 扩层；绿 = `report_metric_binding` 报表闭环；灰 = glossary / 表列挂接。

