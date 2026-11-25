# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-25 · 最新归档：`sessions/tg-rotate-2026-11-25-1137.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 实活必须先落本机 **`.cursor/work-log/当日.md`**；否则 flush/同步只能搬走空壳，双机合并稿也会缺 new-mac 内容（Cursor transcript 不跨机）。
- [LESSON: daily-report,new-mac,automation|关 new-mac 本地权威自动化时，必须保留 pre-daily-report-flush 与 memory-git-sync，否则双机 work-log 断流。]
- 日报链路已定：**21:20（周六 18:20）** 双机 `pre-daily-report-flush` 把当日流水 → `hosts` → `memory-git` 互相同步；**21:30（周六 18:30）** 仅 **old-mac** 合并 hosts、定稿、推 TG。
- 双机全天跑 **memory-git-sync**（约 **120s** 一轮），与定点 flush 并行，不靠单点手动拉。
- **定稿权威仍是 old-mac**；new-mac 设 `WORKLOG_HOST_ID=new-mac`，只负责本机 hosts 导出，不当 TG 推稿主机。
- new-mac 已恢复 **`com.youchu.pre-daily-report-flush`** 与 memory-git-sync；冲刺自检 **`biz=4;thin=0`** 且 hosts 可写才算过关。
- old-mac 必留 **`com.youchu.pre-daily-report-flush`** + **`com.youchu.daily-report-wake`**；核对用 `launchctl list` / 上次退出码 **0**，缺则用对应 **install-*-launchd.sh** 重装。
- 本次 old-mac 两项均已装、已加载、退出码 0，**无需重装**；钟点与定案一致。
- 关 new-mac「权威自动化」时，**不得连带停** pre-daily-report-flush / memory-git-sync（`disable-local-automation-new-mac.sh` 已按此改）。
- TG 派活类问题：先读指定 `prompt_*.md`，直接答文件末尾「当前问题」，避免只复述全文。
- [LESSON: daily-report,dual-mac,work-log|new-mac 干完活必须在 21:20 前写入 `.cursor/work-log/当日.md` 并参与 flush；只停在 transcript 里 old-mac 汇稿必漏，与双机 sync 是否正常无关]
- [LESSON: daily-report,troubleshooting|双机日报缺条先读 `hosts/new-mac/当日.md` 是否空壳/仅 mirror，再查 sync；勿把「漏写流水」误判为「同步又坏了」]
- 双机日报「少内容」要先分清：是 **memory git / hosts 同步失败**，还是 **源机根本没把实活写进可同步文件**。
- 21:20 flush、21:30 定稿前若 `hosts/new-mac`、`hosts/old-mac` 都在且 merge 成功，**不能默认同步又坏了**。
- `hosts/new-mac/当日.md` 若只有「当日未写 `.cursor/work-log`、仅 ops-mirror 兜底」，同步再正常也只能得到**空壳**，不会 magically 带上对话里的活。
- **Cursor transcript 不跨机**；new-mac 上的 IDE 会话 old-mac 扫不到，除非先落到该机 `.cursor/work-log/当日.md` 再经 sprint 点上传。
- 实活在对话/报告文件里、**未进当日 work-log**，权威机（old-mac）定稿时只能写本机可见 + 已同步 hosts，**必然偏窄**。
- old-mac 21:30 定稿并推 TG 后，若完整稿从未进 `youchu-memory` 的 reports/hosts，问题多是 **new-mac 版未进共享定稿链路**，不是 merge 把定稿弄丢。

