# commit 说明禁 bus 编号

**铁律**：`git commit` 说明必须从 diff 从零写业务改动；**禁止**写 `bus#N` / `bus入#N`（与日报禁 bus 同理）。bus 编号只留在 agent-bus / TG 回执。

**怎么拦**：仓库 `.githooks/commit-msg`（需 `git config core.hooksPath .githooks`）。

**2026-11-21**：Away 自动执行多条提交标题带了 bus#（如 14178/14187/14221/14227/14190），已违例；已推远端的不擅自改写历史，之后靠钩子拦。
