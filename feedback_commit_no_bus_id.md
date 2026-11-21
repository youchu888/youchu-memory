# commit 说明禁 bus 编号

**铁律**：`git commit` 说明必须从 diff 从零写业务改动；**禁止**写 `bus#N` / `bus入#N`（与日报禁 bus 同理）。bus 编号只留在 agent-bus / TG 回执。

**根因（2026-11-21）**：修私聊 wake 时重启 `cursor-executor`，启动自愈 `startup kick work` 重放了未结旧单（如全体广播路径对照），结案 commit 标题又粘上 bus#——等于「改 A 又踩已强调的禁重放 / 禁粘 bus」。

**正确做法**
1. 执行面每次调 agent 前注入「commit 禁 bus」铁律（`agent_bus_cursor_executor._COMMIT_NO_BUS_RULE`）。
2. `AGENT_BUS_STARTUP_KICK_WORK` **默认 false**：重启 executor 不 kick 未结 work；真要补跑再显式打开。
3. 钩子兜底：`.githooks/commit-msg` 拦提交说明里的 bus#。
4. 已推远端的违例说明不擅自改历史；以后靠上面三道闸。

**关联**：PINNED「产出物互斥+换轨」· 知秋停重放旧单（当日）· `.githooks/commit-msg`
