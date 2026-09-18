# DolphinScheduler 工作流更新 SOP

适用：通过 DS REST API 改 prod 工作流里某个 task 的 SQL（或其它 taskParams）。

## 0. 配置入口

- DS 接入信息：[`.claude/dolphinscheduler.json`](../../dolphinscheduler.json)（含 default_env / test / prod）；metadata 服务通过 `Settings.load_dolphinscheduler_config(env)` 读取
  - prod base_url: `http://18.141.232.237:12345/dolphinscheduler`
  - test base_url: `http://43.212.183.54:12345/dolphinscheduler`
- 鉴权：HTTP header `token: <token>`
- DS 版本：3.x（Spring Boot；swagger UI 有，api-docs 未暴露）

## 1. 整体流程

```
1. 拉项目/工作流元信息（GET）
2. 拉工作流详情（GET process-definition）
3. 检查 schedule cron + 当前运行 instance（"调度安全窗口"约束，见 §3）
4. 对比仓库 / 在线脚本（diff）
5. 工作流下线（POST .../release OFFLINE）
6. PUT 更新工作流（全量 taskDefinitionJson）
7. 工作流上线（POST .../release ONLINE）  ← 也可在 PUT payload 里直接传 ONLINE 一并完成
8. schedule 上线（POST .../schedules/{id}/online）
9. 验证：先单时段补数 → 跑通后全时段补数（见 §4）
```

## 2. API 参考（DS 3.x）

### 2.1 项目 / 工作流

| 用途 | Method + Path |
|---|---|
| 列项目 | `GET /projects?pageNo=1&pageSize=20` |
| 工作流轻量列表 | `GET /projects/{projectCode}/process-definition/list` |
| 工作流详情（**最关键**） | `GET /projects/{projectCode}/process-definition/{wfCode}` |

**详情 response 关键字段**：
- `data.processDefinition`：工作流元信息（name / releaseState / version / globalParams / locations / tenantCode / executionType / timeout / scheduleReleaseState）
- `data.taskDefinitionList`：所有 task 数组（每个含 `taskParams.sql`）
- `data.processTaskRelationList`：DAG 边数组（preTaskCode / postTaskCode）

### 2.2 release（工作流上下线）

```
POST /projects/{proj}/process-definition/{wfCode}/release
form: releaseState=OFFLINE   # 或 ONLINE
```

返回 `{"code":0,"success":true}` 即成功。

### 2.3 PUT 更新工作流（全量替换）

```
PUT /projects/{proj}/process-definition/{wfCode}
form fields:
  name                    工作流名（原样回传）
  description             描述（原样回传）
  globalParams            全局参数 JSON 字符串（原样回传）
  locations               节点坐标 JSON 字符串（原样回传）
  timeout                 超时秒（原样回传，默认 0）
  tenantCode              ⚠️ 必须填**存在的** tenant，None / 'default' 都会报 "tenant not exists"
                          → 通过 `GET /tenants/list` 拿一个有效 code（如 'root'）
  executionType           PARALLEL / SERIAL（原样回传）
  releaseState            ONLINE / OFFLINE（payload 里也能控制最终状态，PUT 后立即生效）
  taskDefinitionJson      ⚠️ 全量 task 数组的 JSON 字符串。漏一个就丢一个，所有 task 必须原样回传
  taskRelationJson        全量 DAG 边数组的 JSON 字符串
```

**关键规则**：
- **PUT 是全量替换**，不能只传一个 task
- **不动的 task 从 GET response 原样塞回 taskDefinitionJson**，不能从仓库本地文件覆盖
  - 原因：仓库 SQL 跟海豚常有微小差异（占位符引号、注释、空格），海豚那份是经过实测能跑的事实版本，不能被仓库未实测版本覆盖
  - 仓库相当于设计文档，海豚是运行版本
- 序列化时 `taskDefinitionJson` 用 `json.dumps(tasks, ensure_ascii=False)`，再 form-encode

### 2.4 schedule 上下线

```
GET  /projects/{proj}/schedules?processDefinitionCode={wfCode}&pageNo=1&pageSize=20
POST /projects/{proj}/schedules/{scheduleId}/online
POST /projects/{proj}/schedules/{scheduleId}/offline
```

**注意**：schedule 跟 process-definition 不是同一对象。
- **工作流 OFFLINE 时 schedule 会被自动 OFFLINE**（DS 联动行为）
- **工作流再 ONLINE 时 schedule 不会自动 ONLINE**（必须手工再 POST `/schedules/{id}/online`）

所以每次 OFFLINE → PUT → ONLINE 流程之后，schedule 必跟一次 online；不能假定它跟着上来。

### 2.5 补数据 / 启动实例（含单 task 触发）

```
POST /projects/{proj}/executors/start-process-instance
Content-Type: application/x-www-form-urlencoded
form:
  processDefinitionCode    必填，工作流 code
  scheduleTime             ⚠️ 必须 JSON 字符串：{"complementStartDate":"YYYY-MM-DD HH:MM:SS","complementEndDate":"YYYY-MM-DD HH:MM:SS"}
                           旧逗号分隔语法 (DS 2.x/3.0.x) 在 3.1+ 不能用，会报 50014 "start process instance error"
  failureStrategy          END / CONTINUE
  warningType              NONE / SUCCESS / FAILURE / ALL
  warningGroupId           0
  execType                 COMPLEMENT_DATA     # 补数据 — 单 task 模式必须用这个
                           START_PROCESS + startNodeList 是非法组合，报 50014
  runMode                  RUN_MODE_SERIAL / RUN_MODE_PARALLEL
  processInstancePriority  MEDIUM
  workerGroup              default
  environmentCode          ⚠️ 必填 -1（不传报 50014，错误信息不提示是哪个字段缺）
  complementDependentMode  OFF_MODE / ALL_DEPENDENT
  startNodeList            (单 task / 子集触发)指定 task code，多 code 用逗号分隔
  taskDependType           (配合 startNodeList) TASK_ONLY = 只跑 startNodeList，跳过 DEPENDENT 上游
                           TASK_PRE = 跑前置依赖
                           TASK_POST = 跑下游
  dryRun                   0 / 1（1 不真跑、只校验参数；推荐先用 1 试通过再 0 实跑）
```

**单 task 触发示例**（绝对推荐用法）：
```bash
curl -X POST -H "token: <token>" \
  --data-urlencode "processDefinitionCode=21284117013504" \
  --data-urlencode 'scheduleTime={"complementStartDate":"2026-05-06 01:30:00","complementEndDate":"2026-05-06 01:30:00"}' \
  --data-urlencode "failureStrategy=END" \
  --data-urlencode "warningType=NONE" \
  --data-urlencode "warningGroupId=0" \
  --data-urlencode "execType=COMPLEMENT_DATA" \
  --data-urlencode "runMode=RUN_MODE_SERIAL" \
  --data-urlencode "processInstancePriority=MEDIUM" \
  --data-urlencode "workerGroup=default" \
  --data-urlencode "environmentCode=-1" \
  --data-urlencode "complementDependentMode=OFF_MODE" \
  --data-urlencode "startNodeList=21417591806208" \
  --data-urlencode "taskDependType=TASK_ONLY" \
  --data-urlencode "dryRun=0" \
  "<host>/projects/<proj>/executors/start-process-instance"
```

效果：只跑 startNodeList 里那 1 个 task，DEPENDENT 上游全跳过，其他 SQL task 不动。test 环境 dws_app_retention_h 已验证。

**关键陷阱**（每条都踩过）：
1. **scheduleTime 不传 JSON** — 50014，错误信息不提示原因
2. **environmentCode 不传** — 50014
3. **execType=START_PROCESS + startNodeList** — 50014（startNodeList 只跟 COMPLEMENT_DATA 配）
4. **整个工作流补数据 vs 单 task 触发的区别**：
   - 不带 startNodeList：触发整个 DAG，所有 flag=YES task 都跑。如果有 INSERT OVERWRITE PARTITION 类 task，会把当前 slot 时间窗外的数据擦掉
   - 带 startNodeList + TASK_ONLY：只跑指定 task，对其他 task 0 副作用

## 3. 调度安全窗口约束 ⚠️

**操作前必查**：

```
当前时间 vs 下一次 cron 触发时间
```

如果距离下次触发 < N 分钟（建议 N = 5），或者**当前已有运行中 instance**：

1. **不能动**工作流（PUT / release / 删任何 task）
2. 等当前 instance 结束 + cron 触发完成
3. 或者主动 OFFLINE schedule，停掉本周期触发，再操作

**为什么**：
- DS 触发实例时会快照 process-definition 当前 version
- 如果 PUT 跟 cron 撞车，可能让正在跑的实例用旧版 / 新版混合 task，状态不可预期
- 改完工作流再 ONLINE，下次 cron 才会用新版本

**怎么查**：

```python
# 1. 查 schedule cron
GET /projects/{proj}/schedules?processDefinitionCode={wf}
# response.data.totalList[0].crontab → 解析下次触发时间

# 2. 查正在运行的 instance
GET /projects/{proj}/process-instances?stateType=RUNNING_EXECUTION&processDefineCode={wf}
# 如有非空结果 → 等待
```

## 4. 验证流程：先小后大

更新工作流后**不要立刻全量补数**。按 task 的写入语义评估：

| 写入语义 | 补数策略 |
|---|---|
| `INSERT INTO`（增量幂等） | 安全。先跑最早 1 个时段验证，再扩到全时段 |
| `INSERT OVERWRITE PARTITION` | **每次只跑一个 partition**，先一个验证；同 partition 重跑会清空再重写，**不可中途打断** |
| Primary Key UPSERT | 接近增量，但 sod/eod 类字段可能因运行顺序不同而不一致 |
| AGGREGATE BITMAP | 跨 segment 自动 union；同一 dt 多次跑只增加 segment，不会膨胀 |

**最早 1 个时段** = task 当天调度的第一个 slot 时间窗：
- hourly：[T 00:00, T 01:00)
- daily：T 一整天 [T 00:00, T+1 00:00)

跑完查 `WHERE update_time = '<本次跑的时间>'` 过滤验证：
- 数据规模符合上游 dwd 的对应窗口
- 列序、聚合关系守恒
- 与 dwd 同口径对账误差在容忍范围

**验证 OK** 后再补全部时段（hourly 是 24 个，daily 视范围）。

## 5. 实操示例（dws_app_user_d_h hourly task 修复列错位）

参考 [pending_tasks_2026-05-06.md](../reports/pending_tasks_2026-05-06.md)：

1. GET 工作流 `dws_小时` (code=21284117013504)，确认 12 个 task / DAG
2. 对比线上 d_h SQL vs 仓库 [`dws_app_user_d_h_hourly.sql`](../../../ops_system/04.dws/dws_app_user_d_h/dws_app_user_d_h_hourly.sql)：列错位（active 在前 new 在后），仓库版列序对的
3. 检查 schedule：cron `0 30 * * * ? *`，next 触发距离当前 > 5 分钟 → 安全
4. 构造 PUT payload：从 GET response 深拷贝 12 个 task，只把 d_h task 的 `taskParams.sql` 替换为新版本
5. 校验 11 个非目标 task 序列化字节级一致（`json.dumps(o, sort_keys=True) == json.dumps(n, sort_keys=True)`）
6. POST release OFFLINE → PUT 更新（tenantCode='root'）→ release ONLINE
7. POST schedule 95 online
8. 等下次 cron 触发 / 单 task 补数据，单段 segment 验证
9. 全时段补数（用 dws_日.d_h INSERT OVERWRITE PARTITION 修复整个 partition）

## 6. 常见错误

| 现象 | 原因 |
|---|---|
| `tenant not exists` | PUT 里 tenantCode 填了 None / 不存在的值。改成 `GET /tenants/list` 里的真实 code（如 root） |
| PUT 后丢 task | taskDefinitionJson 没传全，丢的会从工作流移除 |
| schedule 不触发 | 工作流 ONLINE 但 schedule OFFLINE。要单独 POST `/schedules/{id}/online` |
| `query schedule list paging error` (10080) | 当前 token 权限不够。备用：直接看 process-definition.scheduleReleaseState 字段 |
| 占位符替换后 SQL 报错 | DS 把 `${var}` 字符串替换不加引号。SQL 里要写 `'${var}'` 或 `CAST('${var}' AS DATETIME)` |
| `EmptyStackException` at TimePlaceholderUtils | SQL 文本（**包括注释**）里出现 `$[...]` 字面量，DS 盲扫整段 SQL 解析时间表达式失败。注释里禁止写 `$[yyyy-MM-dd HH:00:00-1H]` 这类示例 |
| DS 时间表达式 `-1H` 报错 | DS 不识别 `-1H`；减一小时用 `-1/24`；减一分钟用 `-1/24/60` |
| start-process-instance 报 50014 "start process instance error" | 错误信息不提示原因，常见 4 类：①`scheduleTime` 用旧逗号格式而非 JSON；②`environmentCode` 没传；③`execType=START_PROCESS` 跟 `startNodeList` 混用（startNodeList 只跟 COMPLEMENT_DATA 配）；④`tenantCode` 不存在 |

## 7. 维护约定

- 这份 SOP 是元数据管理工具的依赖文档；任何 DS API 行为变化或新坑要回写到这里
- 文档语义要让工具能机器解析（API 路径 / 参数 / response 字段都用代码块标注）
- 操作前的安全检查（§3）是硬约束，工具实现时必须检查后才能 PUT
