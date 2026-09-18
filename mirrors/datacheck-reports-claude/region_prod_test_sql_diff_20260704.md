# region 标准化 · prod(仓库) vs test 海豚 SQL diff

**对照说明**: prod 海豚 API 对本账号 403；prod 侧用 **git 仓库当前 SQL**（知秋 prod 发包同源）。test 为海豚 test 环境 live SQL。
**范围**: dim_region* + 7张带 region 的 DWS task

## 汇总（待狂人/知秋点头后再动 test）

| # | task | code | 对齐 | test region逻辑 | prod region逻辑 | 差异说明 |
|---|------|------|------|----------------|----------------|----------|
| 1 | dim_region_all | 174729505868610 | ❌ | 未识别 | 未识别 | 同逻辑族但全文不一致(注释/格式/其他块) |
| 2 | dim_region_info_all | 174729505868613 | ❌ | hash直算(旧) | hash直算(旧) | 同逻辑族但全文不一致(注释/格式/其他块) |
| 3 | dim_user_all_region_std | 22204399763200 | ❓ | xwalk(COALESCE→geonameid) | 无仓库对照 | 仓库无独立文件，仅记录test逻辑 |
| 4 | dws_app_user_d_h_hourly | 174729505012544 | ❌ | 透传上游region | xwalk(COALESCE→geonameid) | prod已xwalk标准化，test未同步 |
| 5 | dws_app_user_d_h_daily | 174729603403588 | ❌ | 透传上游region | xwalk(COALESCE→geonameid) | prod已xwalk标准化，test未同步 |
| 6 | dws_app_user_w_d_new | 174729603403584 | ❌ | 透传上游region | 透传上游region | 同逻辑族但全文不一致(注释/格式/其他块) |
| 7 | dws_app_user_m_d_new | 174729603403585 | ❌ | 透传上游region | 透传上游region | 同逻辑族但全文不一致(注释/格式/其他块) |
| 8 | dws_app_retention_d_h_hourly | 174729505012546 | ✅ | 透传上游region | 透传上游region |  |
| 9 | dws_app_retention_d_h_daily | 174729603403587 | ❌ | 透传上游region | 透传上游region | 同逻辑族但全文不一致(注释/格式/其他块) |
| 10 | dws_app_order_d_h_hourly | 174729505012545 | ❌ | 透传上游region | xwalk(COALESCE→geonameid) | prod已xwalk标准化，test未同步 |
| 11 | dws_app_order_d_h_daily | 174729603403586 | ❌ | 透传上游region | xwalk(COALESCE→geonameid) | prod已xwalk标准化，test未同步 |

**需同步 test**: 9 项；**已一致**: 1 项

## 需同步明细

### dim_region_all (`174729505868610`)
- gap: 同逻辑族但全文不一致(注释/格式/其他块)
- test片段: `INSERT INTO dim.dim_region_all`
- prod片段: `INSERT INTO dim.dim_region_all`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dim_region_all.diff`

### dim_region_info_all (`174729505868613`)
- gap: 同逻辑族但全文不一致(注释/格式/其他块)
- test片段: `INSERT into dim.dim_region_info_all; select xx_hash3_64(CONCAT_WS('-',CONCAT_WS('-', country_name, NULLIF(province_name, ''), NULLIF(city_name, '')))) AS region,`
- prod片段: `INSERT into dim.dim_region_info_all; select xx_hash3_64(CONCAT_WS('-',CONCAT_WS('-', country_name, NULLIF(province_name, ''), NULLIF(city_name, '')))) AS region,`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dim_region_info_all.diff`

### dws_app_user_d_h_hourly (`174729505012544`)
- gap: prod已xwalk标准化，test未同步
- test片段: `region,; COALESCE(d.region, 99999999) AS region,`
- prod片段: `region,; COALESCE(x.region, 99999999) AS region,`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_user_d_h_hourly.diff`

### dws_app_user_d_h_daily (`174729603403588`)
- gap: prod已xwalk标准化，test未同步
- test片段: `region,; COALESCE(d.region, 99999999) AS region,`
- prod片段: `region,; COALESCE(x.region, 99999999) AS region,`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_user_d_h_daily.diff`

### dws_app_user_w_d_new (`174729603403584`)
- gap: 同逻辑族但全文不一致(注释/格式/其他块)
- test片段: `(`week`, `start_of_week`, `app_code`, `channel`, `region`, `device`, `user_type`,; h.app_code, h.channel, h.region, h.device, h.user_type,`
- prod片段: `(`week`, `start_of_week`, `app_code`, `channel`, `region`, `device`, `user_type`,; h.region,`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_user_w_d_new.diff`

### dws_app_user_m_d_new (`174729603403585`)
- gap: 同逻辑族但全文不一致(注释/格式/其他块)
- test片段: `(`month`, `first_of_month`, `app_code`, `channel`, `region`, `device`, `user_type`,; h.app_code, h.channel, h.region, h.device, h.user_type,`
- prod片段: `(`month`, `first_of_month`, `app_code`, `channel`, `region`, `device`, `user_type`,; h.region,`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_user_m_d_new.diff`

### dws_app_retention_d_h_daily (`174729603403587`)
- gap: 同逻辑族但全文不一致(注释/格式/其他块)
- test片段: `region,; region,`
- prod片段: `region,; region,`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_retention_d_h_daily.diff`

### dws_app_order_d_h_hourly (`174729505012545`)
- gap: prod已xwalk标准化，test未同步
- test片段: `COALESCE(d.region, 99999999) AS region,; LEFT JOIN dim.dim_region_info_all d`
- prod片段: `COALESCE(x.region, 99999999) AS region,; LEFT JOIN dim.dim_geo_region_xwalk x`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_order_d_h_hourly.diff`

### dws_app_order_d_h_daily (`174729603403586`)
- gap: prod已xwalk标准化，test未同步
- test片段: `SELECT uid, app_id, channel, UPPER(user_type) AS user_type, region AS user_region; COALESCE(ut.user_region, 99999999) AS region,`
- prod片段: `COALESCE(x.region, 99999999) AS region,; LEFT JOIN dim.dim_geo_region_xwalk x`
- diff文件: `reports/region_prod_test_sql_diff_20260704/dws_app_order_d_h_daily.diff`
