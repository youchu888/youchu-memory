# 指标库 · ads+dws 填数进度 · 2026-09-22 晚

> test metadata · 未灌 prod

## 已完成

| 阶段 | 结果 |
|------|------|
| 第一批活跃域 | ✅ published 301→322；primary 切到现网有数表 |
| 剩余扫表 candidate | ✅ ~970 条进 staging（`batch_rest_20260922`） |
| 升档（续跑中多次 checkpoint） | ✅ 大部分已落库 |

## 最近一次可达库快照（隧道断前）

| 项 | 数 |
|----|----|
| published | **602** |
| orphaned | 11 |
| active implementation | **~1046** |
| candidate promoted | **582** |
| candidate pending | **~343**（含比率 hold + 弱特征列） |
| rejected_non_metric | 45 |

相对开干前（published 301 / impl 419）：concept +301，实现约 +627。

## 未收口原因

升档脚本在跑剩余 ~200 条时，**堡垒机 `43.213.80.248:22` SSH 超时**，本机 `13306` 隧道断掉。检查点前的写入已 commit，未丢。

## 续跑（隧道恢复后）

```bash
ssh -f -N -L 13306:172.31.6.193:3306 ubuntu@43.213.80.248
export METADATA_MYSQL_URL='mysql+pymysql://admin:...@127.0.0.1:13306/metadata?charset=utf8mb4'
python3 docs/metric_library_batch_rest_promote_20260922.py --apply
```

脚本幂等：已挂列会跳过，只消化剩余 pending。

## 有意未自动升 published

- 比率/avg 列（`ratio_hold`）：避免瞎建 derived
- 无指标名特征的弱度量列：留在 candidate pending
- 影子/备份表：从未纳入范围
