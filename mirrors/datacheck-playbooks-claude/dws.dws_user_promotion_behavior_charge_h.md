# dws.dws_user_promotion_behavior_charge_h 数据核查剧本

## 1. 表信息
- 表名：`dws.dws_user_promotion_behavior_charge_h`
- 业务别名：**渠道充值表（小时）**
- 状态：上线
- 粒度：`hour + dt + channel + app_id + uid`（DUPLICATE KEY）
- 指标字段：`recharge_amount / vip_charge_amount / deduction_vip_charge_amount / coin_charge_amount`（`decimal(18,2)`）
- 与 behavior_h 关系：4 金额字段应与 `dws_user_promotion_behavior_h` 同 `(hour, dt, channel, app_id, uid)` 完全一致。

## 2. 与主剧本的关系

**核查规则一律复用** [dws.dws_user_promotion_behavior_d.md](dws.dws_user_promotion_behavior_d.md)。

本表特有点：
- 小时核对默认覆盖**昨天 + 今天**（`dt IN (T-1, T)`），今天取已到达的小时分区。
- 仅 4 金额字段。part_02 的小时切片是本表的主战场：`charge_h vs behavior_h` 应每小时 4 字段逐格相等，否则需 part_04 归因。
- `charge_h` ↔ `charge_d` 的日小时汇总一致性核对用主剧本 part_01（charge 子集）。

## 3. 核查入口

- `/datacheck dws.dws_user_promotion_behavior_charge_h` → 执行主剧本 part_01（charge 子集） + part_02 的小时段（昨 + 今） + part_03 头部 app。
- 过滤：`channel IS NOT NULL AND channel != 'organic'`；合法 app_id `^[A-Za-z]+-[0-9]+$`。

## 4. 报告落地
- 默认路径：`.claude/database/reports/dws.dws_user_promotion_behavior_charge_h/`
- 或与主表复用同一目录（批次核查）
