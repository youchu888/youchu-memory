# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-24 · 最新归档：`sessions/tg-rotate-2026-07-24-0620.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 设备标签 #5.2 进度同步应分三块：**已完成**（验数结论+补数区间+行数+指标 sanity）、**卡点**（待拍板/环境阻塞）、**下一步**（stage/依赖项），便于群聊一眼扫清
- SF-81 Paimon 试点验数 PASS 后，宽表 `calc_dt=07-20` 约 11.1 万行；核查重点看 **avg7/15/30 未塌缩**、**lifecycle 分布正常**
- TG/群消息发送若 **urllib 超时**，kill 后改 **curl** 重发；勿让 hung 请求占着
- 群旁听 `@mudan99_bot` 的 device `unknown` 质疑：device 为公共字段、清洗后仅四值；查 **dimuser 脚本**溯源，勿凭宽表侧猜测
- [LESSON: page-stay,launchd,agent-bus|停 18:00 页面停留推狂人须卸载 `com.youchu.page-stay-18h` launchd，勿只改脚本不卸定时]
- [LESSON: daily-report,upload|日报上传云端须主人显式指令；只传 `reports/日报-YYYY-MM-DD.md` 定稿全文，禁止改字或夹带其它文件]
- DWM 四表 27 天补数（06-24~07-20）已完成；代码 `bbd40f38` 已推 `origin/dev`，平台 session `dev-20260719-001` 已到 **stage4**
- **卡点①**：`uid_map`（`dev-20260720-001`）是否与宽表并行，需知秋拍板后再并行推进
- **卡点②**：集群 `hadoop-1` 无 sbt，Scala 改动只能 rsync 旧 jar；需装 sbt 或走 **CI 编新 jar** 才能跟进
- prod 海豚 `dws_user_tag_d_d` 单挂后补跑，T-1 约 **11.6 亿行**恢复——单挂定位+补跑是日报级可写成果
- 停 18:00 页面停留推狂人：卸载 launchd **`com.youchu.page-stay-18h`**；手动验数用 `PAGE_STAY_FORCE=1` 跑脚本，恢复定时用 `install-page-stay-18h-launchd.sh`
- 日报流程：**先**读 work-log + transcript + 派单来源 → 落 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` → **仅主人明说「上传云端」**才调上传脚本
- 云端上传只读定稿 Markdown **原封不动** POST `report/submit`；同日同类型覆盖；核对时说明文件路径、类型、日期、工号即可
- prod 海豚晨检：`get_running_summary` + 当日 `FAILURE` 实例；先判「整 wf 挂」还是「单 task 挂」
- `dws_user_tag_d_d` 在 **`wf_ads_日报表_日`**，不在 `wf_dws_汇总_日`；查失败勿只盯 dws 汇总 wf
- 同 wf 其它 task 全 SUCCESS、仅 1 task FAIL → 优先怀疑该 task 瞬时问题，非全链路/SQL 口径
- 17 秒即 FAIL** 不像 OOM（内存爆通常跑更久）；较像 SR 连接池/内存瞬时竞争
- `fail_retry_times=0` 一次失败即标 wf FAILURE；防复发可设 1~2 次重试，或与最重 ads 任务错开几分钟

