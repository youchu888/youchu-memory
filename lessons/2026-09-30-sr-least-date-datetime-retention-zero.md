# SR LEAST(DATE, DATE_SUB) 导致次留全 0

## 现象
周/月汇总次留 SUM=0，手工 BITMAP cohort 非 0。

## 根因
`DATE_SUB` 常返回 DATETIME；与 DATE 进 `LEAST` 类型错乱，区间变空。

## 做法
写 `LEAST(end_dt, DATE(DATE_SUB(biz_dt, INTERVAL 1 DAY)))`。
另：周一 biz 次留下界>上界 → 0 属口径；验收用周中/周末 schedule。

## tags
`starrocks` `LEAST` `retention` `channel_promotion` `stage4`
