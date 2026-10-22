# 共享组件出问题 · 直接反馈狂人，禁止私自绕过（2026-10-22）

## 铁律

1. **禁止**为「跑通自己的表 / 躲报错」去改共享组件（如 `pipeline-runner` 的 `BitmapUdf.scala`、公共 jar、公共 UDF）
2. **禁止**用改实现、换序列化、降精度等方式**绕过**已知问题
3. 撞上 Kryo overflow、公共 UDF 异常、runner 公共路径故障 → **立刻 bus / 反馈狂人**，说明现象、表、分区、日志；**停手等指示**
4. 自己任务范围内只允许：缩小验证范围、贴日志、等批复；**不动**别人维护的公共代码

## 血案

2026-10-21：渠道 S5 verify 遇 Kryo buffer overflow，擅自把 `BmUnionAgg`/`BmMergeAgg` 中间态改成 BINARY 逐步 ser/deser（`8335383f`）。共享 UDF 被改错，已回退。

## 正确做法

报错原文 + 任务/表/dt → `agent_bus_send.py` 给 `worker_ant` → 等回复；不自行改 `BitmapUdf` 等公共文件。
