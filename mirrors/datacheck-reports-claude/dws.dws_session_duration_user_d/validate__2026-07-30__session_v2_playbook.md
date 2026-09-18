# validate · dws_session_duration_* v2 · 2026-07-30

session: dev-20260729-002
env: test（playbook）/ prod（schema only）

## part_01 关键列
PASS — 两表均有 stat_grain / avg_session_duration_sec / avg_daily_duration_sec / duration_bucket / session_cnt / bounce_cnt

## part_02 T-1 两 grain
PASS —
- user session cnt=3822 session_cnt_sum=484572 entity=355845
- user daily cnt=2726 entity=252254
- device session cnt=3420 session_cnt_sum=1116673 entity=983210
- device daily cnt=2379 entity=538448

## part_03 daily 无 bucket0
PASS — user bad=0 / device bad=0

## prod
- 表已存在且含 stat_grain 等 v2 列；当前 0 行（待 prod 海豚发布后补数）
- prod dolphin 尚无 dws_session_duration_* task（search count=0）

## test dolphin
- user task 22357755272832 / device 22357755654144 在 wf_dws_汇总_日，live SQL 含 stat_grain + UNION ALL + 双均值列
- deprecated daily tasks 已不在 wf（404 / search 0）
