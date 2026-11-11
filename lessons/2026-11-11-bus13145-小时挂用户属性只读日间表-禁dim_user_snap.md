# 小时挂用户属性只读日间表（禁 dim_user_snap）

- **日期**: 2026-11-11
- **来源**: bus#13145 · 狂人→全体 · 知秋已定
- **tags**: hourly, dim_user_snap, dwm_user_attr_intraday_d_d, user-attr

## 规则

1. **小时任务**给事件挂用户属性：一律读 `dwm.dwm_user_attr_intraday_d_d`，`dt='D'`，按 `(app_id, uid)` LEFT JOIN。**不读** `dim.dim_user_snap`。
2. **作废**：旧「小时读 `dim_user_snap` snap_dt=D-1，再叠加日间表」。快照约 18 亿行，每小时全扫多花 3 分多钟。
3. 日间表可直接取：渠道、注册时刻、地区、设备、VIP、uid_code。编排里日间表同格先跑完，小时任务以其水位为探针。
4. 关联不上：日间表只收当天有注册/登录/浏览的用户；其它事件用户找不到 → 属性按兜底值。
5. **天任务不变**：仍读 `dim_user_snap`，`snap_dt='D'`。

## 又初侧核验（bus#13145）

- 又初名下无小时 SQL 读 snap，无需改稿。
- 名下天任务读 snap 保持：`ads_channel_metrics_daily_d`、`dws_app_event_funnel_d_d_daily_stage_metrics`。
- 仓内仍旧口径小时稿（非又初 owner）：b2_summary / b2_deduction / b3_behavior / b3_charge hourly。
