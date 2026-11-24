# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-24 · 最新归档：`sessions/tg-rotate-2026-11-24-2236.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- [LESSON: daily-report,dual-mac,work-log|new-mac 干完活必须在 21:20 前写入 `.cursor/work-log/当日.md` 并参与 flush；只停在 transcript 里 old-mac 汇稿必漏，与双机 sync 是否正常无关]
- [LESSON: daily-report,troubleshooting|双机日报缺条先读 `hosts/new-mac/当日.md` 是否空壳/仅 mirror，再查 sync；勿把「漏写流水」误判为「同步又坏了」]
- 双机日报「少内容」要先分清：是 **memory git / hosts 同步失败**，还是 **源机根本没把实活写进可同步文件**。
- 21:20 flush、21:30 定稿前若 `hosts/new-mac`、`hosts/old-mac` 都在且 merge 成功，**不能默认同步又坏了**。
- `hosts/new-mac/当日.md` 若只有「当日未写 `.cursor/work-log`、仅 ops-mirror 兜底」，同步再正常也只能得到**空壳**，不会 magically 带上对话里的活。
- **Cursor transcript 不跨机**；new-mac 上的 IDE 会话 old-mac 扫不到，除非先落到该机 `.cursor/work-log/当日.md` 再经 sprint 点上传。
- 实活在对话/报告文件里、**未进当日 work-log**，权威机（old-mac）定稿时只能写本机可见 + 已同步 hosts，**必然偏窄**。
- old-mac 21:30 定稿并推 TG 后，若完整稿从未进 `youchu-memory` 的 reports/hosts，问题多是 **new-mac 版未进共享定稿链路**，不是 merge 把定稿弄丢。
- 已修链路是：**先双机 flush + sync，再汇稿推 TG**；今晚链路通 ≠ 各机 **21:20 前落流水** 已到位。
- 排查顺序：看当日 `hosts/*` 正文 → 对照是否写过 `.cursor/work-log/当日.md` → 再查 flush/sync 日志与推送主机/时间。
- 用户手里的「3 条完整稿」若只存在于私聊/单机会话，要 **覆盖定稿 + 按需 force 重推 TG**，不能指望事后 sync 自动补齐。
- 日报差异归因话术：**同步 OK + 源机流水缺失**，避免反复改 sync 脚本却治不了漏写。
- 群聊学习可拆成「全停」与「只关私聊推送、后台静默沉淀」；改前需主人明确二选一，勿默认全关。
- 「每日学习」停用要分清两条链路：`worker-ant-daily-learn`（又初·每日学习 → 狂人）与 `daily-group-learn`（凌晨 02:00 群聊学习私聊汇总）；只卸前者时主人仍可能每天收到推送。
- 用户说「取消了还在发」时，先核 launchd/plist 是否 `disabled`、末次推送日期，再对照仍在跑的 job 实际文案，避免混称两条任务。
- 狂人「发了 bus」→ 先入站查 `bus#N`、出站 ack/reply、`processed`；结案则不是「没收到」。
- 口头发 bus 与 agent-bus 入站是同一单；查收以 inbox + 本地状态为准，不以口头提醒为准。
- 「机器人里没看到」要先查 TG `status_mirror` 是否已有入站原文、工作状态、又初出站；有记录则链路正常，问题在观感或注意力。

