# 用户与设备基础表使用说明

> 适用：生产 paimon。表结构取自 2026-11-04 现网 `SHOW CREATE TABLE`，分区范围取自同日 `$partitions`。
> 起草：狂人 · 知秋 2026-11-04 审过

## 一、先记住这几条

1. **用户维度只读 `dim.dim_user_snap`，并且必须带 `snap_dt` 分区。**
   - 不读 `dim_user_all_d`，这张表已作废、即将停更。
   - 不读视图 `dim_user_all_d_v`，视图只供人工查看最新一天。
2. **用户唯一键是 `(app_id, uid)`。** 去重、计数都按这两列，不能只按 uid。
3. **设备只认 sdk_init。**
   - 设备全表、设备日间表只收发生过 sdk_init 的设备。
   - 其他事件里带的设备号不算设备规模。
4. **渠道不重算。**
   - 用户渠道直接取日间表或快照的 `channel`。
   - 设备渠道直接取设备全表的 `channel`。
   - 业务 SQL 里不要再自己做"真实渠道优先"。
5. **要做 bitmap，就用字典号。**
   - 用户号 `uid_code`、设备号 `device_code` 在每个 app 内都从 1 起连续编号，只增不改。
   - 必须和 `app_id` 一起用，单独一个号没有意义。
6. **报表读日结后的数据，不读小时版。** 设备日间表的小时刷新只供观察，对账以日结为准。

## 二、表清单

| 表 | 主体 | 粒度 / 唯一键 | 分区 | 什么时候可用 | 现存分区 |
|---|---|---|---|---|---|
| `dim.dim_user_snap` | 用户 | 每天全量一人一行 · `(app_id, uid)` | `snap_dt` | 第 D 天分区在 D+1 日 00 点那一轮跑完后可用 | 09-27 ~ 11-03（38 个） |
| `dwm.dwm_user_attr_intraday_d_d` | 用户 | 当天活跃用户一人一行 · `(dt, app_id, uid)` | `dt` | 每小时累积，第 D+1 天 00 点那一轮后才是完整的一天 | 08-12 ~ 今天 |
| `dim.dim_device_snap` | 设备 | 每天全量一台一行 · `(snap_dt, app_id, device_id)` | `snap_dt` | 第 D 天分区在 D+1 日 07 点那一轮跑完后可用 | 10-14 ~ 11-03（21 个） |
| `dwm.dwm_device_intraday_d_d` | 设备 | 当天活跃设备一台一行 · `(dt, app_id, device_id)` | `dt` | 小时版每小时覆盖当天；第 D 天在 D+1 日 07 点日结后定稿 | 10-14 ~ 今天 |
| `dwm.dwm_device_uid_rel_d_d` | 设备×用户 | 当天设备与账号关系 · `(dt, app_id, device_id, uid)` | `dt` | D+1 日 07 点日结后 | 10-01 ~ 11-03 |
| `dwm.dwm_device_order_paid_d` | 设备×订单 | 当天支付事件 · `(dt, app_id, event_id)` | `dt` | D+1 日 07 点日结后 | 10-01 ~ 11-03 |
| `dim.dim_uid_code_h` | 用户号表 | 每小时出现的 uid 及其号 | `dt, hh` | 每小时 | 只保留 30 天 |
| `dim.dim_device_code_h` | 设备号表 | 每小时出现的设备及其号 | `dt, hh` | 每小时 | 只保留 30 天 |

时间一律是北京时间。

## 三、用户基础表

### 3.1 `dim.dim_user_snap`：用户全表按天快照

每个 `snap_dt` 分区装当天全部用户，一人一行。历史分区全部保留。

**怎么读**

- 天任务算第 D 天：读 `snap_dt = 'D'`。
- 日间表 / 小时任务算第 D 天：读 `snap_dt = 'D-1'`，因为第 D 天的快照要等这一天结束后才出来。
- 在 SQL 里先用 `assert_true` 校验目标分区存在、行数大于 0，再往下算。这样分区没出来时任务会直接失败，不会拿空数据或别的日期去算。
- 重跑历史日期时，分区跟着任务日期走，不会读错日期。这也是不许读视图的原因：视图永远指向最新一天。

**主要字段**

| 字段 | 含义 |
|---|---|
| `app_id`, `uid` | 唯一键 |
| `uid_code` | 用户字典号，每个 app 内从 1 连续、< 2^32、只增不改；怪 uid 为 NULL |
| `channel` | 归因后的渠道，兜底 organic |
| `register_channel` | 注册渠道原值（未归因），兜底 organic |
| `register_time` | 注册时刻；没有注册记录的兜底为 2025-12-20 00:00:00 |
| `register_attribution_flag` | 注册归因标记，兜底 0 |
| `user_type` | VIP / NORMAL，兜底 NORMAL |
| `country` / `province` / `city` | 地区，兜底"其他" |
| `region` | 标准地区 ID，未命中为 99999999 |
| `device` | IOS / ANDROID / PC / OTHER |
| `device_brand` / `device_model` | 注册时的设备品牌、型号，不兜底 |
| `first_recharge_time` | 首次支付时刻（amount>0 的首笔） |
| `last_login_time` | 末次登录时刻；从未登录为 NULL，不拿注册时刻顶替 |
| `is_paid_ever` / `first_pay_date` / `first_pay_amount` / `last_pay_date` / `last_pay_amount` | 支付首末信息，金额单位为分 |
| `is_vip_ever` / `first_vip_date` / `first_vip_amount` / `last_vip_date` / `last_vip_amount` | VIP 购买首末信息，金额单位为分 |
| `row_update_time` | 本行写入时刻 |
| `snap_dt` | 快照日，分区列 |

另有 `last_active_time`、`lifecycle_stage`、`last_recharge_*`、`first_recharge_amount/type`、`vip_expire_time` 等列，这些列没有注释，含义沿用老用户总表。

**注意**

- 第 D 天快照 = 第 D-1 天快照 + 第 D 天的变更。改了某一天，后面每一天都要顺着重跑，所以下游发现快照有问题，要报给我，不要自己改。
- 用 `uid_code` 做人数 bitmap 时，怪 uid 没有号，不会被算进去。怪 uid 指 null、-1、undefined 这类不指向具体某个人的值，这是有意排除的。

### 3.2 `dwm.dwm_user_attr_intraday_d_d`：用户日间属性表

当天有活动的用户一人一行，每小时累积，24 轮跑完就是当天全量。它是用户快照唯一的上游。

**主要字段**：`channel`（当天渠道，已按既定规则确定）、`register_channel`、`device_os` / `device_brand` / `device_model`、地区、`register_time`、`user_type`（当天任一浏览是 VIP 即算 VIP）、`user_type_eod`（取当天最后一条浏览的状态）、`first_event_time` / `last_event_time`、`last_login_time`、`is_new`（当天有注册）、`logged_in`、`pv_cnt`、`uid_code`。

**注意**

- `ordered_today` 已停止进数，恒为 NULL，不要用。
- `ord_channel_norm`、`univ_channel_norm` 是算渠道用的辅助列，业务不要用。
- 当轮发号失败时 `uid_code` 也可能为 NULL。要用号，以快照表为准。

### 3.3 用户号表 `dim.dim_uid_code_h` / `dim.dim_uid_code_d`

这两张表记录发号过程，只保留 30 天，不是全量字典。下游要用号时，直接取快照表或日间表上的 `uid_code`，不要拿号表去 join。

## 四、设备基础表

### 4.1 `dim.dim_device_snap`：设备全表按天快照

每个 `snap_dt` 分区装截至当天的全部 sdk_init 设备，一台一行。数据从 10-14 起。

**主要字段**

| 字段 | 含义 |
|---|---|
| `app_id`, `device_id` | 唯一键（设备号原值） |
| `device_code` | 设备字典号，每个 app 内从 1 连续、只增不改 |
| `channel` | 设备渠道：第一次出现的真实渠道；从没出现过真实渠道的记 organic。由 organic 改成真实渠道只会发生一次 |
| `channel_updated_time` | channel 改为真实渠道的那条事件时间；organic 为 NULL |
| `first_seen_dt` / `first_seen_time` / `first_seen_event` / `first_seen_channel` | 首次出现的日期、时刻、事件和当天渠道 |
| `platform` / `os_family` / `device` / `device_brand` / `device_model` / 地区 | 首次出现那天的值 |
| `first_sdk_init_*` | 第一次 sdk_init 的溯源：时间、event_id、到达时间、渠道、来源与当前页面的域名和路径、IP、UA |
| `create_time` | 新登记时刻，登记后不改 |
| `row_update_time` | channel 最近一次变化的时刻 |

**怎么读**：和用户快照一样，带 `snap_dt` 读。做新设备统计时，取 `first_seen_dt = snap_dt` 的行。

### 4.2 `dwm.dwm_device_intraday_d_d`：设备日间表

当天有活动的 sdk_init 设备一台一行，只记当天事实，不放累计值。

- **小时版**：每小时从当天 0 点重算到这个小时为止，覆盖当天分区，只供观察。
- **日结**：第 D+1 天 03:00 之后，把第 D 天整天重算一遍，迟到的数据收到 03:00 为止，之后这一天不再改。报表和对账以日结后的数据为准。

**主要字段**：`device_code`、`channel`（当天最早的真实渠道，**不是设备渠道**，设备渠道要取全表）、`platform` / `os_family` / `device` / `device_brand` / `device_model` / 地区（sdk_init 优先）、`pv_cnt` / `login_cnt` / `register_cnt` / `paid_cnt` / `sdk_init_cnt`（按 event_id 去重的事件数）、`first_event_time` / `first_event` / `first_sdk_init_time` / `last_event_time`。

### 4.3 `dwm.dwm_device_uid_rel_d_d`：设备-账号关系日表

记录当天哪台设备上出现过哪个 uid，每天只写一次。

- `device_code`：不是 SDK 采集的设备为 NULL。
- `uid_code`：怪 uid 为 NULL。
- 各类事件次数：`cnt_user_register` / `cnt_user_login` / `cnt_app_page_view` / `cnt_order_paid`。
- 其他字段：`first_rel_*` / `last_rel_*`、`did_corroborated`。
- 10-01 ~ 10-13 的分区是老链路写的，`device_code` / `uid_code` 全为空（10-05、10-13 实查）；从 10-14 起才有号。

### 4.4 `dwm.dwm_device_order_paid_d`：设备支付明细

当天的支付事件一条一行，唯一键是 `(dt, app_id, event_id)`。`order_id` 不唯一。

- 金额：`amount_fen` 单位为分，不可解析时为 NULL；`currency` 恒为 CNY。
- 订单属性：`order_type`（coin_purchase / vip_subscription）、`pay_type`、`pay_channel`、`channel`、`device`。
- 号列：`device_code` / `uid_code`，规则同关系表；uid 为空时 `uid_code` 也为 NULL。
- 10-01 ~ 10-13 同样号列全为空，从 10-14 起才有号。

### 4.5 设备号表 `dim.dim_device_code_h`

和用户号表一样，只记录发号过程，只保留 30 天。下游取号要用全表或日间表上的 `device_code`。

## 五、下游怎么用（场景对照）

| 我要算 | 读哪张 | 关键写法 |
|---|---|---|
| 某天用户属性、渠道、是否付费 | `dim_user_snap` | `snap_dt = 'D'`，按 `(app_id, uid)` 关联 |
| 小时任务给事件挂用户属性 | `dim_user_snap` | `snap_dt = 'D-1'`，再叠加当天日间表 |
| 某天活跃用户 | `dwm_user_attr_intraday_d_d` | `dt = D`，要等 D+1 日 00 点后才是全天 |
| 用户人数 bitmap | 快照或日间表的 `uid_code` | 按 `app_id` 分组；怪 uid 不计入 |
| 设备规模、新设备 | `dim_device_snap` | `snap_dt = 'D'`；新设备取 `first_seen_dt = snap_dt` |
| 某天活跃设备、设备事件次数 | `dwm_device_intraday_d_d` | `dt = D`，D+1 日 07 点日结后再读 |
| 设备渠道 | `dim_device_snap.channel` | 不用日间表的 channel |
| 一台设备上有哪些账号 / 一个账号用过哪些设备 | `dwm_device_uid_rel_d_d` | `dt = D` |
| 按设备看支付 | `dwm_device_order_paid_d` | `dt = D`，金额单位为分 |

## 六、调度时间（生产 pipeline-runner）

| 时间 | 做什么 |
|---|---|
| 每小时 | 用户：订单去重 → 用户发号 → 用户日间表。设备：设备发号 → 设备日间表（小时版）。 |
| 00 点那一轮 | 用户快照 `dim_user_snap` 出第 D-1 天的分区 |
| 04:30 | 用户、设备字典每日核对（失败只告警，不挡其他线） |
| 07 点那一轮 | 设备日结四步：日间表日结 → 设备全表 → 关系日表 → 支付明细 |

遇到数据问题，报给狂人。
