# dws.dws_user_promotion_behavior_charge_d 数据核查剧本

## 1. 表信息
- 表名：`dws.dws_user_promotion_behavior_charge_d`
- 业务别名：**渠道充值表（日）**
- 状态：上线
- 粒度：`dt + channel + app_id + uid`（DUPLICATE KEY）
- 指标字段：`recharge_amount / vip_charge_amount / deduction_vip_charge_amount / coin_charge_amount`（`decimal(18,2)`）
- 与 behavior 表关系：充值子集投影，同 `(dt, channel, app_id, uid)` 的 4 金额字段应与 `dws_user_promotion_behavior_d` 完全一致。

## 2. 与主剧本的关系

**核查规则一律复用** [dws.dws_user_promotion_behavior_d.md](dws.dws_user_promotion_behavior_d.md)。

本表特有点：
- 仅 4 金额字段，没有 `is_*` / `consume_amount` / 行为计数，part_01 只比 4 金额字段。
- `charge_d` ↔ `charge_h` 的日小时汇总一致性核对用主剧本 part_01。
- `charge_d` ↔ `behavior_d` 的同名金额交叉核对用主剧本 part_02。

## 3. 核查入口

- `/datacheck dws.dws_user_promotion_behavior_charge_d` → 执行主剧本 part_01（charge 子集） + part_02 的天侧 + part_03 的头部 app。
- 默认参数：`target_dt = T-1`。
- 过滤：`channel IS NOT NULL AND channel != 'organic'`；合法 app_id `^[A-Za-z]+-[0-9]+$`。

## 4. 报告落地
- 默认路径：`.claude/database/reports/dws.dws_user_promotion_behavior_charge_d/`
- 或与主表复用同一目录（批次核查）
