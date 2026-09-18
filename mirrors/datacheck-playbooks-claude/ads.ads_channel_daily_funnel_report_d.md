# ads.ads_channel_daily_funnel_report_d 数据核查剧本

## 1. 表信息
- 表名：`ads.ads_channel_daily_funnel_report_d`
- 业务名：渠道漏斗日报
- 状态：上线
- 粒度：`dt + app_id + channel + device_type + user_type`
- 绑定 ADS 程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/05.ads/ads_channel_daily_funnel_report_d.sql`
- 绑定 DWS 程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_channel_daily_funnel_d.sql`

## 2. 使用前提
- 该表是多行为漏斗汇总表，用户可能只发生部分行为，不发生其他行为。
- 因此对账时必须接受“目标为 0、来源无记录/NULL”的情况，将其视为正常，不应直接判错。
- 该表不适合每次都做全量重算；默认采用“结构全量 + 指标抽样 + 已知高风险字段专项核对”的方式。
- 当前已确认一个程序映射问题：ADS SQL 中 `pay_gold_uid_bm` 被错误映射成 `pay_user_vip_count`，开发修复后应专项复核 `pay_user_gold_count`。

## 3. 默认参数
- `dt`：必填，默认取目标表最新分区日期
- `app_id` / `channel`：选填；如需抽样，优先覆盖大盘 app、organic 渠道、已发现差异样本 app

## 4. 核查顺序

### part_01 基础形态与过滤逻辑
目标：先确认 ADS 表本身结构正常。

检查项：
1. 主键粒度 `dt + app_id + channel + device_type + user_type` 唯一
2. 主键字段无空值
3. `device_type` 仅允许 `IOS / ANDROID / PC / OTHER`
4. `user_type` 仅允许 `NEW / OLD`
5. 不存在应被 ADS 过滤掉的全零行

建议 SQL 要点：
- 统计总行数、主键去重行数
- 统计空主键行数、非法枚举行数
- 统计核心指标全为 0 的残留行数

### part_02 ADS 投影与字段映射专项核查
目标：优先发现 ADS 层字段别名或投影错误。

检查项：
1. `pay_user_gold_count` 是否仍被错误映射
2. `pay_user_count / pay_user_vip_count / pay_user_gold_count` 与 DWS bitmap 投影是否一致
3. `revenue_total / revenue_vip / revenue_gold` 与 DWS 聚合字段是否一致
4. `order_launch_count / repurchase_user_count / user_consume_gold` 投影是否一致

说明：
- 如果字段映射错误已确认，不需要重复跑大量全量 SQL 证明；记录为已知 bug，并在开发修复后回归。

### part_03 指标抽样来源对账
目标：对其余指标做抽样重算，而不是全量硬扫。

抽样原则：
1. 优先抽样大盘 app + `organic`
2. 优先抽样已出现过差异的 app/渠道/设备/新老组合
3. 每类指标保留 10~20 组样本即可，不追求每次全量覆盖

建议分组：
1. 内容 UV：`video_play_uv` / `novel_play_uv` / `comic_play_uv` / `total_play_uv`
2. 支付与金额：`pay_user_count` / `pay_user_vip_count` / `pay_user_gold_count` / `revenue_*`
3. 订单与复购：`order_launch_count` / `repurchase_user_count`
4. 金币消耗：`user_consume_gold`
5. `dad_count`：仅做抽样，不做“全量 mismatch 行数 = 错误量”式判断

对账原则：
- 以当前程序实现口径为准，而不是先按业务解释改写口径。
- 对账时使用 `COALESCE(..., 0)`，将 `NULL` 与无来源记录的 0 视为同义。
- 只把“非 NULL/0 类的实际数值不等”记为硬差异。

### part_04 表内 sanity
目标：快速筛出明显不合理关系。

检查项：
- `total_play_uv >= video_play_uv / novel_play_uv / comic_play_uv`
- `pay_user_count >= pay_user_vip_count`
- `pay_user_count >= pay_user_gold_count`（修复后复核）
- `repurchase_user_count <= pay_user_count`
- `revenue_total >= revenue_vip`
- `revenue_total >= revenue_gold`
- `video_play_uv <= dad_count` 是否大面积失真
- `video_play_uv > 0` 但 `video_play_progress_ratio = 0` 的样本是否集中
- `comic_play_uv > 0` 但 `comic_play_progress_ratio = 0` 的样本是否集中
- `play_video_count > 0` 但 `total_play_duration = 0` 的样本是否集中

说明：
- 这些 sanity 主要用于发现字段映射错位、来源口径分裂或明显逻辑反转。

### part_05 来源事件质量专项（视频/漫画）
目标：识别“有消费事件但进度/时长异常”的来源埋点问题，并区分是 ADS 计算问题还是 DWD 源事件本身问题。

数据来源表：
- `dwd.dwd_app_page_view_d`
- `dwd.dwd_video_event_h`
- `dwd.dwd_comic_event_d`

处理程序：
- ADS：`/ops_system/05.ads/ads_channel_daily_funnel_report_d/ads_channel_daily_funnel_report_d.sql`
- DWS：`/ops_system/04.dws/dws_channel_daily_funnel_d/dws_channel_daily_funnel_d.sql`

检查项：
1. 抽样检查 `video_play_uv > 0` 但 `video_play_progress_ratio = 0` 的组合，回查 `dwd.dwd_video_event_h.play_progress/play_duration` 原始样本。
2. 抽样检查 `play_video_count > 0` 但 `total_play_duration = 0` 的组合，确认原始事件是否普遍 `play_duration = 0/NULL`。
3. 抽样检查 `comic_play_uv > 0` 但 `comic_play_progress_ratio = 0` 的组合，回查 `dwd.dwd_comic_event_d.read_progress` 是否原始值即接近 0 或字段量纲过小。
4. 统计 `page_device_uv = 0` 但 `video_device_uv > 0` 的 app / 组合，识别 page/video 链路口径分裂。
5. 统计 `dwd.dwd_video_event_h` 在 `dt` 当天按 `app_id + uid + video_id` 去重后：
   - `play_progress IS NULL` 占比
   - `play_duration IS NULL OR = 0` 占比
   用于评估来源视频埋点质量。

去重口径：
- 质量统计默认按 `app_id + uid + video_id` 去重。
- 同一组重复事件，仅保留 `MAX(play_progress)` 与 `MAX(play_duration)` 作为该组最终值。

判断原则：
- 若 ADS 与 DWS 对账一致，但异常样本在 DWD 原始事件中已存在，则归类为“来源数据问题”，不判定为 ADS 计算 bug。
- 若 `page_device_uv = 0` 且 `video_device_uv > 0`，优先判定为 page/video 采集链路不一致。
- 若漫画原始 `read_progress` 值域极小且目标字段为整数，需标记“来源量纲/字段类型设计风险”。

### part_06 结论输出规范
报告必须把结果分开写：
1. 已确认程序 bug
2. 抽样通过的指标
3. 存在硬差异、需继续跟进的指标
4. 暂不应直接判错的指标（如 `dad_count` 这类易受骨架/稀疏行为影响的项）
5. 已确认的来源数据质量问题（如 `play_progress` / `play_duration` / `read_progress` 异常）

## 5. 当前已知结论（2026-04-03）
- `pay_user_gold_count`：ADS 字段映射错误，属确定性程序 bug
- `novel_play_uv`、`revenue_vip`、`revenue_gold`、`user_consume_gold`：本轮已通过
- `video_play_uv`、`pay_user_count`、`revenue_total`、`order_launch_count`、`repurchase_user_count`：出现少量硬差异，适合后续抽样复核
- `dad_count`：不应使用全量 mismatch 行数直接定义错误量，应按抽样 + `NULL/0` 同义方式判断

## 6. 维护约定
- 如果 ADS/DWS 程序的字段映射、设备归一、新老判定或事件来源变更，需同步更新本剧本。
- 开发修复 `pay_user_gold_count` 后，应优先回归：
  1. `pay_user_gold_count`
  2. `pay_user_count`
  3. `pay_user_vip_count`
  4. 表内支付类 sanity
