# 红线续篇 · 提审可见与海豚绑定

35. **request-publish 前：禁冲掉 owned；归档须先 uncomplete** — `PUT /full` 必须合并保留 `dolphin_owned_tasks`（含 env=test）与完整 `target`；已产发归档的 session 先 `POST .../uncomplete` 再提审，否则野花「待我审核」看不到、向导 Step2 报不可同步。见 `feedback_dev_session_no_fake_stage_done.md` · lesson `2026-11-04-request-publish禁冲owned与先解归档.md`。

35b. **Spark 提审/S7 前必核 `stage4_spark.mount`** — 向导只认 state 里的 mount，不认 testcluster 现网；`PUT /full` 冲掉 mount 会表现为「S4 还没挂过调度」。提审前 GET 断言 mount.ok；改 state 必须合并。见 lesson `2026-11-04-request-publish禁冲owned与先解归档.md` · `2026-11-07-spark-s7-提审前mount与state合并检查.md`。
