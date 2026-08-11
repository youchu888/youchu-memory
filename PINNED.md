# 红线 pinned（冷启动硬注入 · 上限 30 条）

> 违反易出事故 / 一天内被纠正 ≥2 次的规矩。只写**一行结论**，细节进 feedback/lesson。  
> 维护：又初 · 与 `.cursor/rules` 对齐；增删后下次 sessionStart 自动进 bootstrap。

1. **prod 海豚/写库不自发** — 须审核人（狂人/知秋等）；默认只做 test。
2. **禁止改插件 version / 自打自装 vsix** — 只报 bug；官方包由野花下发。
3. **已定规矩先确认再改** — feedback/rules 破例须用户明确说「改」。
4. **提交即 push** — 说入库/commit 成功后立刻 `git push`（除非用户禁止）。
5. **commit 第一人称直述** — 禁「我/主人/旁白体」。
6. **Dev Session 1–6 禁空标 done** — 每 stage 要有产物与证据；stage7 等审核。
7. **datacheck 默认只查 T-1** — 用户未指定日期禁止扫多日。
8. **agent-bus：60s ACK → 干完 reply 才结案** — 禁拉取时 mark_processed。
9. **固定流程先跑 runbook** — 归因/补数等禁止对话里从零造轮子。
10. **INSERT 必须显式列名** — 防列错位（尤其加列后）。
11. **StarRocks：禁 `$[yyyyMMdd]` 类宏进直连 SQL** — 用字面量或会话变量。
12. **核查认可后写回 playbook** — lesson 记坑；playbook 记可跑步骤。
13. **工作簿以最新一日为准** — 读到新簿立刻更新 `project_youchu_workbook_tasks.md`。
14. **群聊仅显式 @初儿/@又初 才回** — 裸喊名/探活收条不回。
15. **日报只写已完成 + 通俗书面** — 禁 bus#；推送仅 old-mac。
16. **健壮性优先** — 失败可自愈、不滚雪球、改完当场 smoke。
17. **记忆：沉前查重；日常 append；勿用 upsert 当 append**。
18. **记忆召回：动前先查；打开≠用了；真改做法才 touch**。
19. **冷启动别只看 hot** — 必须同时看「按时间最近动过」。
20. **提交范围** — 默认只动 `ops_system` 等业务目录；禁擅自改平台插件/api_v1。
