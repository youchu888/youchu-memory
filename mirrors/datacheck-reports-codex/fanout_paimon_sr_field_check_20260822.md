# Fanout Paimon vs SR 字段抽样检查（2026-08-22）

## 结论（先看这里）

| 检查项 | 结果 |
|--------|------|
| Paimon 相对 manifest **缺列** | **无**（38 张 `sinks.paimon!=false` 表均齐全） |
| Paimon 相对 SR 同名字段 **缺列** | **无**（SR 侧多为无 `_r` 批表；新增 device/system/trace 等列多数 **SR 本身没有**） |
| 核心写入 `device` / `device_id` / `etl_time` | **正常**（抽样分区空值率约 **0%**） |
| 易空字段 | `user_agent`、`trace_id`、`recommend_trace_id` 常近 **100% 空**；`device_fingerprint` / `device_brand` / `system_*` 因表而异（源端稀疏，非缺列） |
| Fanout→SR sink | 现网 **关闭**（`fanout.sink.starrocks.enabled=false`）；对账对象为 SR `dwd.*`（去 `_r`） |

说明：抽样 5 行若刚好都空，会标 `FOCUS_EMPTY`；以分区空值率为准更可靠（见 Details）。

范围：manifest 中 `sinks.paimon!=false` 的表；Paimon=`dwd.*_r`，SR 优先同名 `_r`，否则去 `_r`。
抽样：每表最多 5 行（优先 dt=2026-08-22，其次 2026-08-21）。

## Summary

| table | status | SR | miss_manifest | miss_vs_SR | focus_all_empty_sample |
|-------|--------|----|---------------|------------|------------------------|
| dwd_ad_click_h_r | FOCUS_EMPTY | dwd_ad_click_h | - | - | user_agent,trace_id |
| dwd_app_page_click_d_r | FOCUS_EMPTY | dwd_app_page_click_d | - | - | recommend_trace_id |
| dwd_app_page_view_d_r | FOCUS_EMPTY | dwd_app_page_view_d | - | - | user_agent,recommend_trace_id,trace_id |
| dwd_app_install_d_r | FOCUS_EMPTY | dwd_app_install_d | - | - | user_agent |
| dwd_coin_consume_h_r | FOCUS_EMPTY | dwd_coin_consume_h | - | - | device_fingerprint,device_brand,device_model,system_name,system_version,trace_id |
| dwd_comic_event_d_r | FOCUS_EMPTY | dwd_comic_event_d | - | - | user_agent,recommend_trace_id,trace_id |
| dwd_keyword_click_d_r | OK | dwd_keyword_click_d | - | - | - |
| dwd_keyword_search_d_r | FOCUS_EMPTY | dwd_keyword_search_d | - | - | search_trace_id,trace_id |
| dwd_landing_page_click_r | FOCUS_EMPTY | dwd_landing_page_click | - | - | device_fingerprint |
| dwd_landing_page_click_d_r | FOCUS_EMPTY | dwd_landing_page_click_d | - | - | user_agent |
| dwd_landing_page_view_d_r | FOCUS_EMPTY | dwd_landing_page_view_d | - | - | user_agent,trace_id |
| dwd_novel_event_d_r | FOCUS_EMPTY | dwd_novel_event_d | - | - | user_agent,recommend_trace_id,trace_id |
| dwd_order_created_h_r | FOCUS_EMPTY | dwd_order_created_h | - | - | device_fingerprint,user_agent,device_brand,device_model,system_name,system_version,trace_id |
| dwd_order_paid_d_r | FOCUS_EMPTY | dwd_order_paid_d | - | - | device_fingerprint,user_agent,device_brand,device_model,system_name,system_version,trace_id |
| dwd_user_login_d_r | FOCUS_EMPTY | dwd_user_login_d | - | - | device_fingerprint |
| dwd_user_login_d_v2_r | FOCUS_EMPTY | dwd_user_login_d_v2 | - | - | device_fingerprint,user_agent,device_brand,device_model,system_name,system_version,trace_id |
| dwd_user_register_d_r | FOCUS_EMPTY | dwd_user_register_d | - | - | device_fingerprint |
| dwd_user_register_d_v2_r | FOCUS_EMPTY | dwd_user_register_d_v2 | - | - | user_agent,device_brand,device_model,system_name,system_version,device_fingerprint |
| dwd_user_watch_video_r | OK | dwd_user_watch_video | - | - | - |
| dwd_video_collect_d_r | FOCUS_EMPTY | dwd_video_collect_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_video_comment_d_r | FOCUS_EMPTY | dwd_video_comment_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_video_event_h_r | FOCUS_EMPTY | dwd_video_event_h | - | - | recommend_trace_id,user_agent,trace_id |
| dwd_video_like_d_r | FOCUS_EMPTY | dwd_video_like_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_video_purchase_d_r | FOCUS_EMPTY | dwd_video_purchase_d | - | - | recommend_trace_id,device_fingerprint,device_brand,device_model,system_name,system_version,trace_id |
| dwd_ad_click_sdk_d_r | OK | dwd_ad_click_sdk_d | - | - | - |
| dwd_ad_request_d_r | FOCUS_EMPTY | dwd_ad_request_d | - | - | device_brand,device_model,trace_id |
| dwd_ad_fill_d_r | FOCUS_EMPTY | dwd_ad_fill_d | - | - | device_brand,device_model |
| dwd_ad_close_d_r | FOCUS_EMPTY | dwd_ad_close_d | - | - | user_agent |
| dwd_ad_error_d_r | FOCUS_EMPTY | dwd_ad_error_d | - | - | user_agent,trace_id |
| dwd_ad_impression_sdk_d_r | FOCUS_EMPTY | dwd_ad_impression_sdk_d | - | - | device_brand,device_model |
| dwd_comic_collect_d_r | FOCUS_EMPTY | dwd_comic_collect_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_comic_like_d_r | FOCUS_EMPTY | dwd_comic_like_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_comic_comment_d_r | FOCUS_EMPTY | dwd_comic_comment_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_comic_purchase_d_r | FOCUS_EMPTY | dwd_comic_purchase_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_novel_collect_d_r | FOCUS_EMPTY | dwd_novel_collect_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_novel_like_d_r | FOCUS_EMPTY | dwd_novel_like_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_novel_comment_d_r | FOCUS_EMPTY | dwd_novel_comment_d | - | - | recommend_trace_id,device_fingerprint |
| dwd_novel_purchase_d_r | FOCUS_EMPTY | dwd_novel_purchase_d | - | - | device_fingerprint |

## Details

## dwd_ad_click_h_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_ad_click_h`
- Paimon cols: 35; manifest cols: 35
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent', 'trace_id']`
- focus partition empty rates:
  - device empty=0/2806623 (0.0%)
  - device_id empty=0/2806623 (0.0%)
  - user_agent empty=2806623/2806623 (100.0%)
  - device_brand empty=467016/2806623 (16.6%)
  - device_model empty=467929/2806623 (16.7%)
  - device_fingerprint empty=303934/2806623 (10.8%)
  - system_name empty=600201/2806623 (21.4%)
  - system_version empty=607713/2806623 (21.7%)
  - trace_id empty=2806623/2806623 (100.0%)
  - etl_time empty=0/2806623 (0.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='f9a36813af99fa89e8d16fe17b7fa811', user_agent=None, device_brand='OPPO', device_model='PFVM10', device_fingerprint='16f9f45e84462d01294c7ee88f0340ed5c6f78e17d2bef53b96542a1c8d16927', system_name='Android', system_version='12', trace_id=None, etl_time='2026-08-21 16:16:17.532862'
  - device='android', device_id='a8f0418417901818b3a7e5e757f79edb', user_agent=None, device_brand='vivo', device_model='V2304A', device_fingerprint='f0694636a268689151ae0e1c0e7ec5fecdaec7f318ead679e89656f49471fe8d', system_name='Android', system_version='16', trace_id=None, etl_time='2026-08-21 16:31:43.252296'
- interesting always-empty in sample: `['user_agent', 'trace_id']`

## dwd_app_page_click_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_app_page_click_d`
- Paimon cols: 38; manifest cols: 38
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id']`
- focus partition empty rates:
  - device empty=0/225559753 (0.0%)
  - device_id empty=0/225559753 (0.0%)
  - recommend_trace_id empty=225191989/225559753 (99.8%)
  - device_fingerprint empty=16945285/225559753 (7.5%)
- sample focus values (first 2 rows):
  - device='android', device_id='4be8c5578c887cabaabb9059d162efd6', recommend_trace_id=None, device_fingerprint='1ef18b2869b5e12ea1176bd970b83c7d1d70eb29c553dd84788b3507b6f82a36'
  - device='android', device_id='0832dfc3fef6be28281b88ae8708fdfa', recommend_trace_id=None, device_fingerprint='e1920cf82878c7f365958585b92a6d4424e3f850516f19ecc2e695a9330a0b32'
- interesting always-empty in sample: `['recommend_trace_id']`

## dwd_app_page_view_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_app_page_view_d`
- Paimon cols: 40; manifest cols: 40
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent', 'recommend_trace_id', 'trace_id']`
- focus partition empty rates:
  - device empty=0/52332751 (0.0%)
  - device_id empty=0/52332751 (0.0%)
  - user_agent empty=52332751/52332751 (100.0%)
  - device_brand empty=25446937/52332751 (48.6%)
  - device_model empty=25512457/52332751 (48.8%)
  - recommend_trace_id empty=52065390/52332751 (99.5%)
  - device_fingerprint empty=2241758/52332751 (4.3%)
  - etl_time empty=0/52332751 (0.0%)
  - system_name empty=27324066/52332751 (52.2%)
  - system_version empty=27355433/52332751 (52.3%)
  - trace_id empty=52323992/52332751 (100.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='050088a38f8874592959f110fa7fc3a7', user_agent=None, device_brand='OnePlus', device_model='PHP110', recommend_trace_id=None, device_fingerprint='cad37b2942c2f5f0b8aa3791496967e72e6521f97b5a36389bceac4656d324da', etl_time='2026-08-21 16:25:11.936617', system_name='Android', system_version='13', trace_id=None
  - device='android', device_id='4be8c5578c887cabaabb9059d162efd6', user_agent=None, device_brand='vivo', device_model='V2507A', recommend_trace_id=None, device_fingerprint='1ef18b2869b5e12ea1176bd970b83c7d1d70eb29c553dd84788b3507b6f82a36', etl_time='2026-08-21 16:25:59.929100', system_name='Android', system_version='16', trace_id=None
- interesting always-empty in sample: `['user_agent', 'recommend_trace_id', 'trace_id']`

## dwd_app_install_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_app_install_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent']`
- focus partition empty rates:
  - device empty=0/346314 (0.0%)
  - device_id empty=0/346314 (0.0%)
  - user_agent empty=300108/346314 (86.7%)
  - device_brand empty=28617/346314 (8.3%)
  - device_model empty=28608/346314 (8.3%)
  - trace_id empty=151030/346314 (43.6%)
  - device_fingerprint empty=12461/346314 (3.6%)
  - etl_time empty=0/346314 (0.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='a73319eb656ee5a2c4024bd847becab3', user_agent=None, device_brand='HUAWEI', device_model='CLS-AL00', trace_id='9bff4a15-7604-4fa1-8010-d60b14dc2a97', device_fingerprint='459363516725ff5925a82a4c9b7cea38b4937e3738c383105a770490106fde3c', etl_time='2026-08-21 16:32:14.277570'
  - device='android', device_id='a3c56db0157503fe989cdfdf2ee48136', user_agent=None, device_brand='OPPO', device_model='PHZ110', trace_id='388fb6af-e2cb-4554-b237-282f14defeb2', device_fingerprint='e54b0445436792f1efa8b5802209b35eb7f963d2555b955bfe22f305a78ae0c6', etl_time='2026-08-21 16:17:17.493018'
- interesting always-empty in sample: `['user_agent']`

## dwd_coin_consume_h_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_coin_consume_h`
- Paimon cols: 34; manifest cols: 34
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['device_fingerprint', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`
- focus partial empty in sample: `user_agent=2/5`
- focus partition empty rates:
  - device empty=0/18322 (0.0%)
  - device_id empty=0/18322 (0.0%)
  - device_fingerprint empty=15271/18322 (83.3%)
  - user_agent empty=9959/18322 (54.4%)
  - device_brand empty=7718/18322 (42.1%)
  - device_model empty=7452/18322 (40.7%)
  - system_name empty=8569/18322 (46.8%)
  - system_version empty=9004/18322 (49.1%)
  - trace_id empty=18322/18322 (100.0%)
  - etl_time empty=0/18322 (0.0%)
- sample focus values (first 2 rows):
  - device='PC', device_id='b1be4eb0401a821e50e2b2406ee855cb', device_fingerprint=None, user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, etl_time='2026-08-21 16:32:34.950757'
  - device='PC', device_id='405e95d463caaf4726a0bd60e2e17e24', device_fingerprint=None, user_agent='Go-http-client/2.0', device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, etl_time='2026-08-21 16:27:53.174192'
- interesting always-empty in sample: `['device_fingerprint', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`

## dwd_comic_event_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_comic_event_d`
- Paimon cols: 40; manifest cols: 40
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent', 'recommend_trace_id', 'trace_id']`
- focus partition empty rates:
  - device empty=0/9220453 (0.0%)
  - device_id empty=0/9220453 (0.0%)
  - user_agent empty=9220453/9220453 (100.0%)
  - device_brand empty=660909/9220453 (7.2%)
  - device_model empty=662885/9220453 (7.2%)
  - recommend_trace_id empty=8909523/9220453 (96.6%)
  - trace_id empty=9220453/9220453 (100.0%)
  - device_fingerprint empty=13416/9220453 (0.1%)
  - system_name empty=1205811/9220453 (13.1%)
  - system_version empty=1205825/9220453 (13.1%)
  - etl_time empty=0/9220453 (0.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='db69ad9112fd07b328730e7c4e6fdcd0', user_agent=None, device_brand='HONOR', device_model='ALT-AN00', recommend_trace_id=None, trace_id=None, device_fingerprint='743474b57f7b458ab4fc7fda046c0824c42b491dfd057df42a8e8a6e4ad401a9', system_name='Android', system_version='14', etl_time='2026-08-21 16:36:23.847885'
  - device='android', device_id='4be8c5578c887cabaabb9059d162efd6', user_agent=None, device_brand='vivo', device_model='V2507A', recommend_trace_id=None, trace_id=None, device_fingerprint='1ef18b2869b5e12ea1176bd970b83c7d1d70eb29c553dd84788b3507b6f82a36', system_name='Android', system_version='16', etl_time='2026-08-21 16:25:59.190730'
- interesting always-empty in sample: `['user_agent', 'recommend_trace_id', 'trace_id']`

## dwd_keyword_click_d_r

- status: **OK**
- SR table: `dwd_keyword_click_d`
- Paimon cols: 30; manifest cols: 30
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `-`
- focus partial empty in sample: `user_agent=4/5; device_brand=1/5; device_model=1/5; device_fingerprint=1/5`
- focus partition empty rates:
  - device empty=0/6530815 (0.0%)
  - device_id empty=0/6530815 (0.0%)
  - user_agent empty=5520770/6530815 (84.5%)
  - device_brand empty=777939/6530815 (11.9%)
  - device_model empty=782553/6530815 (12.0%)
  - device_fingerprint empty=369750/6530815 (5.7%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='91209c2f49a0be7f08687bccf0821d4d', user_agent=None, device_brand='vivo', device_model='V2324A', device_fingerprint='458a8345766be2e27fb4e2b6379f3d0728532fc3ec5415a7a85bb63935e3c823'
  - device='IOS', device_id='e357ebfc668ad86885dd06a292687e92', user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5.2 Mobile/15E148 Safari/604.1', device_brand=None, device_model=None, device_fingerprint='fp_cc4e980c'

## dwd_keyword_search_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_keyword_search_d`
- Paimon cols: 34; manifest cols: 34
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['search_trace_id', 'trace_id']`
- focus partial empty in sample: `user_agent=1/5; device_brand=4/5; device_model=4/5; device_fingerprint=2/5; system_name=2/5; system_version=4/5`
- focus partition empty rates:
  - device empty=0/8478223 (0.0%)
  - device_id empty=0/8478223 (0.0%)
  - user_agent empty=3922249/8478223 (46.3%)
  - device_brand empty=2109571/8478223 (24.9%)
  - device_model empty=2119732/8478223 (25.0%)
  - search_trace_id empty=8034010/8478223 (94.8%)
  - device_fingerprint empty=3947677/8478223 (46.6%)
  - system_name empty=2355606/8478223 (27.8%)
  - system_version empty=2491025/8478223 (29.4%)
  - trace_id empty=8478210/8478223 (100.0%)
  - etl_time empty=0/8478223 (0.0%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='dd7a62b7dd533b029c408e0389a56b0e', user_agent=None, device_brand='OnePlus', device_model='PKR110', search_trace_id=None, device_fingerprint='4e3df95d53bd84f4b477dec046727104249b33ae46a26b131dba430c4c777e07', system_name='Android', system_version='16', trace_id=None, etl_time='2026-08-21 16:00:00.556619'
  - device='ANDROID', device_id='f9b823c659abd96682c5a72ebd4df5d7', user_agent='Mozilla/5.0 (Linux; Android 16; PJA110 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/149.0.7827.164 Mobile Safari/537.36;SuiRui/twitter/ver=1.6.2', device_brand=None, device_model=None, search_trace_id=None, device_fingerprint=None, system_name='Android', system_version=None, trace_id=None, etl_time='2026-08-21 16:00:00.187883'
- interesting always-empty in sample: `['search_trace_id', 'trace_id']`

## dwd_landing_page_click_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_landing_page_click`
- Paimon cols: 16; manifest cols: 16
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `ANY` / 5
- focus all-empty in sample: `['device_fingerprint']`
- focus partial empty in sample: `device_brand=3/5`
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='9a09c4f26453b5400b0e0a8b76aa8eee', device_brand=None, device_model='BTK-W00', device_fingerprint=None
  - device='IOS', device_id='c0007c90e3ef491640386abcffec11d8', device_brand='Apple', device_model='iPhone', device_fingerprint=None
- interesting always-empty in sample: `['uid', 'device_fingerprint']`

## dwd_landing_page_click_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_landing_page_click_d`
- Paimon cols: 35; manifest cols: 35
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent']`
- focus partial empty in sample: `device_brand=1/5`
- focus partition empty rates:
  - device empty=0/567104 (0.0%)
  - device_id empty=0/567104 (0.0%)
  - user_agent empty=567104/567104 (100.0%)
  - device_brand empty=301180/567104 (53.1%)
  - device_model empty=100994/567104 (17.8%)
  - system_name empty=5590/567104 (1.0%)
  - system_version empty=9754/567104 (1.7%)
  - trace_id empty=4468/567104 (0.8%)
  - device_fingerprint empty=159649/567104 (28.2%)
  - etl_time empty=0/567104 (0.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='043a5ca18cc32d56f73a6ed1ec456f27', user_agent=None, device_brand='vivo', device_model='V1934A', system_name='Android', system_version='9', trace_id='31ceeb70-b103-45ac-ade2-006234519', device_fingerprint='6718e7ce1d8e92e38bfba113fb30ccfe4c89393eee37d1717383ee269303ff39', etl_time='2026-08-21 16:07:20.285706'
  - device='android', device_id='120b0b83c5fb11561efa611adb4e6708', user_agent=None, device_brand='Meizu', device_model='M2012K10C', system_name='Android', system_version='13', trace_id='06d2edbc-8aab-47a9-adbc-6b2d04e7a', device_fingerprint='673796e84814484a4f3ff5d7fd7c97dfcda4689b644acf4e1977d2de8b27d46b', etl_time='2026-08-21 16:31:58.232000'
- interesting always-empty in sample: `['uid', 'user_agent']`

## dwd_landing_page_view_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_landing_page_view_d`
- Paimon cols: 27; manifest cols: 27
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent', 'trace_id']`
- focus partial empty in sample: `device_brand=2/5`
- focus partition empty rates:
  - device empty=0/594264 (0.0%)
  - device_id empty=0/594264 (0.0%)
  - user_agent empty=594264/594264 (100.0%)
  - device_brand empty=294746/594264 (49.6%)
  - device_model empty=96948/594264 (16.3%)
  - system_name empty=16178/594264 (2.7%)
  - system_version empty=22100/594264 (3.7%)
  - device_fingerprint empty=135365/594264 (22.8%)
  - trace_id empty=560306/594264 (94.3%)
  - etl_time empty=0/594264 (0.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='0227f44d000eb62eee33976cce13df8c', user_agent=None, device_brand='vivo', device_model='V2130A', system_name='Android', system_version='13', device_fingerprint='e9c7994e2c38d3eb492df73a3cab255429c2339f43727ab706cc0db8dbff8825', trace_id=None, etl_time='2026-08-21 16:37:07.766855'
  - device='android', device_id='76caef9280dd39e0dea0ee9d0c56339b', user_agent=None, device_brand='vivo', device_model='V2505A', system_name='Android', system_version='16', device_fingerprint='6e3bf92eae03e7de60e662b116c658ec87c9c36b3bb47e6f4684361debbbf848', trace_id=None, etl_time='2026-08-21 16:19:43.432116'
- interesting always-empty in sample: `['uid', 'user_agent', 'trace_id']`

## dwd_novel_event_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_novel_event_d`
- Paimon cols: 40; manifest cols: 40
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent', 'recommend_trace_id', 'trace_id']`
- focus partition empty rates:
  - device empty=0/436605 (0.0%)
  - device_id empty=0/436605 (0.0%)
  - user_agent empty=436605/436605 (100.0%)
  - device_brand empty=59786/436605 (13.7%)
  - device_model empty=60002/436605 (13.7%)
  - recommend_trace_id empty=432913/436605 (99.2%)
  - trace_id empty=436605/436605 (100.0%)
  - device_fingerprint empty=4910/436605 (1.1%)
  - system_name empty=60968/436605 (14.0%)
  - system_version empty=60968/436605 (14.0%)
  - etl_time empty=0/436605 (0.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='a73319eb656ee5a2c4024bd847becab3', user_agent=None, device_brand='HUAWEI', device_model='CLS-AL00', recommend_trace_id=None, trace_id=None, device_fingerprint='459363516725ff5925a82a4c9b7cea38b4937e3738c383105a770490106fde3c', system_name='Android', system_version='12', etl_time='2026-08-21 16:32:14.278108'
  - device='android', device_id='a73319eb656ee5a2c4024bd847becab3', user_agent=None, device_brand='HUAWEI', device_model='CLS-AL00', recommend_trace_id=None, trace_id=None, device_fingerprint='459363516725ff5925a82a4c9b7cea38b4937e3738c383105a770490106fde3c', system_name='Android', system_version='12', etl_time='2026-08-21 16:32:14.278131'
- interesting always-empty in sample: `['user_agent', 'recommend_trace_id', 'trace_id']`

## dwd_order_created_h_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_order_created_h`
- Paimon cols: 38; manifest cols: 38
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['device_fingerprint', 'user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`
- focus partition empty rates:
  - device empty=0/7210 (0.0%)
  - device_id empty=0/7210 (0.0%)
  - device_fingerprint empty=6348/7210 (88.0%)
  - user_agent empty=3110/7210 (43.1%)
  - device_brand empty=2894/7210 (40.1%)
  - device_model empty=2834/7210 (39.3%)
  - system_name empty=3040/7210 (42.2%)
  - system_version empty=3071/7210 (42.6%)
  - trace_id empty=7210/7210 (100.0%)
  - etl_time empty=0/7210 (0.0%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='NO_DEVICE_ID', device_fingerprint=None, user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, etl_time='2026-08-21 16:17:53.766383'
  - device='ANDROID', device_id='NO_DEVICE_ID', device_fingerprint=None, user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, etl_time='2026-08-21 16:03:30.845656'
- interesting always-empty in sample: `['device_fingerprint', 'user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`

## dwd_order_paid_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_order_paid_d`
- Paimon cols: 36; manifest cols: 36
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['device_fingerprint', 'user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`
- focus partition empty rates:
  - device empty=0/3679 (0.0%)
  - device_id empty=0/3679 (0.0%)
  - device_fingerprint empty=3675/3679 (99.9%)
  - etl_time empty=0/3679 (0.0%)
  - user_agent empty=3061/3679 (83.2%)
  - device_brand empty=3250/3679 (88.3%)
  - device_model empty=3220/3679 (87.5%)
  - system_name empty=3053/3679 (83.0%)
  - system_version empty=3156/3679 (85.8%)
  - trace_id empty=3679/3679 (100.0%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='NO_DEVICE_ID', device_fingerprint=None, etl_time='2026-08-21 16:15:41.871439', user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None
  - device='PC', device_id='NO_DEVICE_ID', device_fingerprint=None, etl_time='2026-08-21 16:00:53.795409', user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None
- interesting always-empty in sample: `['pay_channel', 'device_fingerprint', 'user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`

## dwd_user_login_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_user_login_d`
- Paimon cols: 11; manifest cols: 11
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `ANY` / 5
- focus all-empty in sample: `['device_fingerprint']`
- sample focus values (first 2 rows):
  - device_id='NO_DEVICE_ID', device_fingerprint=None
  - device_id='NO_DEVICE_ID', device_fingerprint=None
- interesting always-empty in sample: `['ip', 'device_fingerprint']`

## dwd_user_login_d_v2_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_user_login_d_v2`
- Paimon cols: 27; manifest cols: 27
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['device_fingerprint', 'user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`
- focus partition empty rates:
  - device empty=0/3355683 (0.0%)
  - device_id empty=0/3355683 (0.0%)
  - device_fingerprint empty=2865260/3355683 (85.4%)
  - etl_time empty=0/3355683 (0.0%)
  - user_agent empty=765738/3355683 (22.8%)
  - device_brand empty=1212272/3355683 (36.1%)
  - device_model empty=1186981/3355683 (35.4%)
  - system_name empty=1139443/3355683 (34.0%)
  - system_version empty=1171037/3355683 (34.9%)
  - trace_id empty=3350678/3355683 (99.9%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='NO_DEVICE_ID', device_fingerprint=None, etl_time='2026-08-21 16:53:34.679441', user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None
  - device='ANDROID', device_id='NO_DEVICE_ID', device_fingerprint=None, etl_time='2026-08-21 16:50:10.473113', user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None
- interesting always-empty in sample: `['device_fingerprint', 'user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`

## dwd_user_register_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_user_register_d`
- Paimon cols: 16; manifest cols: 16
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `ANY` / 5
- focus all-empty in sample: `['device_fingerprint']`
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='NO_DEVICE_ID', device_fingerprint=None
  - device='ANDROID', device_id='a6eb04d7570351422574a83a81dc7dba', device_fingerprint=None
- interesting always-empty in sample: `['device_fingerprint']`

## dwd_user_register_d_v2_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_user_register_d_v2`
- Paimon cols: 28; manifest cols: 28
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'device_fingerprint']`
- focus partial empty in sample: `trace_id=3/5`
- focus partition empty rates:
  - device empty=0/578127 (0.0%)
  - device_id empty=0/578127 (0.0%)
  - user_agent empty=578127/578127 (100.0%)
  - device_brand empty=334532/578127 (57.9%)
  - device_model empty=331960/578127 (57.4%)
  - system_name empty=326352/578127 (56.4%)
  - system_version empty=332607/578127 (57.5%)
  - trace_id empty=237698/578127 (41.1%)
  - device_fingerprint empty=521659/578127 (90.2%)
  - etl_time empty=0/578127 (0.0%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='NO_DEVICE_ID', user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, device_fingerprint=None, etl_time='2026-08-21 16:16:08.859132'
  - device='ANDROID', device_id='NO_DEVICE_ID', user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, device_fingerprint=None, etl_time='2026-08-21 16:17:46.461956'
- interesting always-empty in sample: `['user_agent', 'device_brand', 'device_model', 'system_name', 'system_version', 'device_fingerprint']`

## dwd_user_watch_video_r

- status: **OK**
- SR table: `dwd_user_watch_video`
- Paimon cols: 17; manifest cols: 17
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `-`
- focus partial empty in sample: `device_fingerprint=1/5`
- focus partition empty rates:
  - device empty=0/144609199 (0.0%)
  - device_id empty=0/144609199 (0.0%)
  - device_fingerprint empty=10289767/144609199 (7.1%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='6114adea18fa99773f13b75bd834899b', device_fingerprint='03de6ae76bb62675fd25027cf5002c6b07b8827e2fa723abed45e146446fbdfd'
  - device='ANDROID', device_id='f86d0ecb9855b2ccc33bdf39cce7d893', device_fingerprint=None

## dwd_video_collect_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_video_collect_d`
- Paimon cols: 26; manifest cols: 26
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/554275 (0.0%)
  - device_id empty=0/554275 (0.0%)
  - recommend_trace_id empty=533747/554275 (96.3%)
  - device_fingerprint empty=493310/554275 (89.0%)
- sample focus values (first 2 rows):
  - device='PC', device_id='NO_DEVICE_ID', recommend_trace_id=None, device_fingerprint=None
  - device='PC', device_id='NO_DEVICE_ID', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_video_comment_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_video_comment_d`
- Paimon cols: 26; manifest cols: 26
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/41286 (0.0%)
  - device_id empty=0/41286 (0.0%)
  - recommend_trace_id empty=40714/41286 (98.6%)
  - device_fingerprint empty=39182/41286 (94.9%)
- sample focus values (first 2 rows):
  - device='IOS', device_id='3be95d49d5a2c2c4cdd6c0c1c1668523', recommend_trace_id=None, device_fingerprint=None
  - device='ANDROID', device_id='fc5f7a41ddbff06ebf193deaf9980b2f', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_video_event_h_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_video_event_h`
- Paimon cols: 41; manifest cols: 41
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'user_agent', 'trace_id']`
- focus partition empty rates:
  - device empty=0/128690068 (0.0%)
  - device_id empty=0/128690068 (0.0%)
  - recommend_trace_id empty=124617148/128690068 (96.8%)
  - device_fingerprint empty=6046076/128690068 (4.7%)
  - user_agent empty=70398734/128690068 (54.7%)
  - device_brand empty=52936123/128690068 (41.1%)
  - device_model empty=52989333/128690068 (41.2%)
  - system_name empty=55051309/128690068 (42.8%)
  - system_version empty=55065556/128690068 (42.8%)
  - trace_id empty=128673160/128690068 (100.0%)
  - etl_time empty=0/128690068 (0.0%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='92e29f6323e72c4104788980cdc1c6d9', recommend_trace_id=None, device_fingerprint='cd1116b9732b8e8ec383d735414fca9b987b4e31cf81b999282cc9c5d77389ad', user_agent=None, device_brand='realme', device_model='RMX3357', system_name='Android', system_version='13', trace_id=None, etl_time='2026-08-21 16:30:14.931979'
  - device='ANDROID', device_id='263530fefe5204a51899f91bde9eb1a8', recommend_trace_id=None, device_fingerprint='89dc626256c34b3e7a09bcfe5e5430486f46a99655a0a04b6a84cc8453841255', user_agent=None, device_brand='HONOR', device_model='KOZ-AL00', system_name='Android', system_version='10', trace_id=None, etl_time='2026-08-21 16:35:30.110940'
- interesting always-empty in sample: `['recommend_trace_id', 'user_agent', 'trace_id']`

## dwd_video_like_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_video_like_d`
- Paimon cols: 26; manifest cols: 26
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/487950 (0.0%)
  - device_id empty=0/487950 (0.0%)
  - recommend_trace_id empty=436816/487950 (89.5%)
  - device_fingerprint empty=473910/487950 (97.1%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='09f5c624d034a65b4730ebd5cca74640', recommend_trace_id=None, device_fingerprint=None
  - device='ANDROID', device_id='09f5c624d034a65b4730ebd5cca74640', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_video_purchase_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_video_purchase_d`
- Paimon cols: 34; manifest cols: 34
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`
- focus partial empty in sample: `user_agent=3/5`
- focus partition empty rates:
  - device empty=0/9127 (0.0%)
  - device_id empty=0/9127 (0.0%)
  - recommend_trace_id empty=8963/9127 (98.2%)
  - device_fingerprint empty=8437/9127 (92.4%)
  - user_agent empty=2781/9127 (30.5%)
  - device_brand empty=2615/9127 (28.7%)
  - device_model empty=2410/9127 (26.4%)
  - system_name empty=3446/9127 (37.8%)
  - system_version empty=3624/9127 (39.7%)
  - trace_id empty=9127/9127 (100.0%)
  - etl_time empty=0/9127 (0.0%)
- sample focus values (first 2 rows):
  - device='ANDROID', device_id='9053dfbad69e992b7ffc4f99ab3699de', recommend_trace_id=None, device_fingerprint=None, user_agent=None, device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, etl_time='2026-08-21 16:10:47.188277'
  - device='IOS', device_id='282ab32d1374c0aa1fc4297bcce60785', recommend_trace_id=None, device_fingerprint=None, user_agent='Dart/3.6 (dart:io)', device_brand=None, device_model=None, system_name=None, system_version=None, trace_id=None, etl_time='2026-08-21 16:11:32.955343'
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint', 'device_brand', 'device_model', 'system_name', 'system_version', 'trace_id']`

## dwd_ad_click_sdk_d_r

- status: **OK**
- SR table: `dwd_ad_click_sdk_d`
- Paimon cols: 28; manifest cols: 28
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-21` / 5
- focus all-empty in sample: `-`
- focus partial empty in sample: `user_agent=3/5; device_brand=2/5; device_model=2/5`
- focus partition empty rates:
  - device empty=0/55 (0.0%)
  - device_id empty=0/55 (0.0%)
  - user_agent empty=6/55 (10.9%)
  - device_brand empty=46/55 (83.6%)
  - device_model empty=46/55 (83.6%)
  - trace_id empty=0/55 (0.0%)
  - device_fingerprint empty=0/55 (0.0%)
  - etl_time empty=0/55 (0.0%)
- sample focus values (first 2 rows):
  - device='ios', device_id='55dfb047f387c3714590cb820f6e9eff', user_agent=None, device_brand='Apple', device_model='iPhone', trace_id='2090775174674358272', device_fingerprint='b2c91a9056457b2204107dadb5ecf39e4fce67c8e035869f9041684957e1af8d', etl_time='2026-08-21 12:17:36.170590'
  - device='ios', device_id='55dfb047f387c3714590cb820f6e9eff', user_agent=None, device_brand='Apple', device_model='iPhone', trace_id='2090776533578522624', device_fingerprint='b2c91a9056457b2204107dadb5ecf39e4fce67c8e035869f9041684957e1af8d', etl_time='2026-08-21 12:25:49.585705'

## dwd_ad_request_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_ad_request_d`
- Paimon cols: 28; manifest cols: 28
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['device_brand', 'device_model', 'trace_id']`
- focus partition empty rates:
  - device empty=0/62 (0.0%)
  - device_id empty=0/62 (0.0%)
  - user_agent empty=0/62 (0.0%)
  - device_brand empty=62/62 (100.0%)
  - device_model empty=62/62 (100.0%)
  - trace_id empty=62/62 (100.0%)
  - device_fingerprint empty=0/62 (0.0%)
  - etl_time empty=0/62 (0.0%)
- sample focus values (first 2 rows):
  - device='pc', device_id='271ca3fdcd06eb6c4c2b663f82fb4d5d', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', device_brand=None, device_model=None, trace_id=None, device_fingerprint='d98d277b15292a1404fb7551cbee5b3b862144f93a30cfd035f0e749bcd8cc01', etl_time='2026-08-21 16:06:56.344923'
  - device='pc', device_id='271ca3fdcd06eb6c4c2b663f82fb4d5d', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', device_brand=None, device_model=None, trace_id=None, device_fingerprint='d98d277b15292a1404fb7551cbee5b3b862144f93a30cfd035f0e749bcd8cc01', etl_time='2026-08-21 16:08:11.358650'
- interesting always-empty in sample: `['device_brand', 'device_model', 'trace_id']`

## dwd_ad_fill_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_ad_fill_d`
- Paimon cols: 29; manifest cols: 29
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 2
- focus all-empty in sample: `['device_brand', 'device_model']`
- focus partition empty rates:
  - device empty=0/2 (0.0%)
  - device_id empty=0/2 (0.0%)
  - user_agent empty=0/2 (0.0%)
  - device_brand empty=2/2 (100.0%)
  - device_model empty=2/2 (100.0%)
  - trace_id empty=0/2 (0.0%)
  - device_fingerprint empty=0/2 (0.0%)
  - etl_time empty=0/2 (0.0%)
- sample focus values (first 2 rows):
  - device='pc', device_id='271ca3fdcd06eb6c4c2b663f82fb4d5d', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', device_brand=None, device_model=None, trace_id='2090833347653246976', device_fingerprint='d98d277b15292a1404fb7551cbee5b3b862144f93a30cfd035f0e749bcd8cc01', etl_time='2026-08-21 16:08:11.358664'
  - device='pc', device_id='271ca3fdcd06eb6c4c2b663f82fb4d5d', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', device_brand=None, device_model=None, trace_id='2090833029301379072', device_fingerprint='d98d277b15292a1404fb7551cbee5b3b862144f93a30cfd035f0e749bcd8cc01', etl_time='2026-08-21 16:06:56.320906'
- interesting always-empty in sample: `['device_brand', 'device_model']`

## dwd_ad_close_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_ad_close_d`
- Paimon cols: 30; manifest cols: 30
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-21` / 5
- focus all-empty in sample: `['user_agent']`
- focus partition empty rates:
  - device empty=0/417 (0.0%)
  - device_id empty=0/417 (0.0%)
  - user_agent empty=386/417 (92.6%)
  - device_brand empty=2/417 (0.5%)
  - device_model empty=2/417 (0.5%)
  - trace_id empty=0/417 (0.0%)
  - device_fingerprint empty=0/417 (0.0%)
  - etl_time empty=0/417 (0.0%)
- sample focus values (first 2 rows):
  - device='ios', device_id='55dfb047f387c3714590cb820f6e9eff', user_agent=None, device_brand='Apple', device_model='iPhone', trace_id='2090784145614282753', device_fingerprint='b2c91a9056457b2204107dadb5ecf39e4fce67c8e035869f9041684957e1af8d', etl_time='2026-08-21 12:52:49.833021'
  - device='ios', device_id='55dfb047f387c3714590cb820f6e9eff', user_agent=None, device_brand='Apple', device_model='iPhone', trace_id='2090718972067553280', device_fingerprint='b2c91a9056457b2204107dadb5ecf39e4fce67c8e035869f9041684957e1af8d', etl_time='2026-08-21 08:33:56.425189'
- interesting always-empty in sample: `['user_agent']`

## dwd_ad_error_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_ad_error_d`
- Paimon cols: 31; manifest cols: 31
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-21` / 5
- focus all-empty in sample: `['user_agent', 'trace_id']`
- focus partition empty rates:
  - device empty=0/340 (0.0%)
  - device_id empty=0/340 (0.0%)
  - user_agent empty=26/340 (7.6%)
  - device_brand empty=302/340 (88.8%)
  - device_model empty=302/340 (88.8%)
  - trace_id empty=73/340 (21.5%)
  - device_fingerprint empty=0/340 (0.0%)
  - etl_time empty=0/340 (0.0%)
- sample focus values (first 2 rows):
  - device='ios', device_id='55dfb047f387c3714590cb820f6e9eff', user_agent=None, device_brand='Apple', device_model='iPhone', trace_id=None, device_fingerprint='b2c91a9056457b2204107dadb5ecf39e4fce67c8e035869f9041684957e1af8d', etl_time='2026-08-21 13:49:27.675080'
  - device='ios', device_id='55dfb047f387c3714590cb820f6e9eff', user_agent=None, device_brand='Apple', device_model='iPhone', trace_id=None, device_fingerprint='b2c91a9056457b2204107dadb5ecf39e4fce67c8e035869f9041684957e1af8d', etl_time='2026-08-21 14:13:53.835602'
- interesting always-empty in sample: `['user_agent', 'trace_id']`

## dwd_ad_impression_sdk_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_ad_impression_sdk_d`
- Paimon cols: 32; manifest cols: 32
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 4
- focus all-empty in sample: `['device_brand', 'device_model']`
- focus partition empty rates:
  - device empty=0/4 (0.0%)
  - device_id empty=0/4 (0.0%)
  - user_agent empty=0/4 (0.0%)
  - device_brand empty=4/4 (100.0%)
  - device_model empty=4/4 (100.0%)
  - trace_id empty=0/4 (0.0%)
  - device_fingerprint empty=0/4 (0.0%)
  - etl_time empty=0/4 (0.0%)
- sample focus values (first 2 rows):
  - device='pc', device_id='271ca3fdcd06eb6c4c2b663f82fb4d5d', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', device_brand=None, device_model=None, trace_id='2090833029301379073', device_fingerprint='d98d277b15292a1404fb7551cbee5b3b862144f93a30cfd035f0e749bcd8cc01', etl_time='2026-08-21 16:07:01.501483'
  - device='pc', device_id='271ca3fdcd06eb6c4c2b663f82fb4d5d', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', device_brand=None, device_model=None, trace_id='2090833029301379072', device_fingerprint='d98d277b15292a1404fb7551cbee5b3b862144f93a30cfd035f0e749bcd8cc01', etl_time='2026-08-21 16:06:56.320998'
- interesting always-empty in sample: `['device_brand', 'device_model', 'is_skippable']`

## dwd_comic_collect_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_comic_collect_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/84164 (0.0%)
  - device_id empty=0/84164 (0.0%)
  - recommend_trace_id empty=82525/84164 (98.1%)
  - device_fingerprint empty=83933/84164 (99.7%)
- sample focus values (first 2 rows):
  - device='android', device_id='941379704057317575fc34e0588f8838', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='941379704057317575fc34e0588f8838', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_comic_like_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_comic_like_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/29531 (0.0%)
  - device_id empty=0/29531 (0.0%)
  - recommend_trace_id empty=29531/29531 (100.0%)
  - device_fingerprint empty=29500/29531 (99.9%)
- sample focus values (first 2 rows):
  - device='android', device_id='6ad6d08446966970de965a52c873f289', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='0b0639c1104dfff01d23540f1428b77f', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_comic_comment_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_comic_comment_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/2283 (0.0%)
  - device_id empty=0/2283 (0.0%)
  - recommend_trace_id empty=2283/2283 (100.0%)
  - device_fingerprint empty=2258/2283 (98.9%)
- sample focus values (first 2 rows):
  - device='android', device_id='cbec512bb17a42956b72e085aa04a889', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='cbec512bb17a42956b72e085aa04a889', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_comic_purchase_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_comic_purchase_d`
- Paimon cols: 28; manifest cols: 28
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/670 (0.0%)
  - device_id empty=0/670 (0.0%)
  - recommend_trace_id empty=669/670 (99.9%)
  - device_fingerprint empty=269/670 (40.1%)
- sample focus values (first 2 rows):
  - device='android', device_id='e09448d834c2793d3fd7b20b17532d92', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='8411ad00fd3ce4352563dcaff0d7d9d7', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_novel_collect_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_novel_collect_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/13458 (0.0%)
  - device_id empty=0/13458 (0.0%)
  - recommend_trace_id empty=13337/13458 (99.1%)
  - device_fingerprint empty=13393/13458 (99.5%)
- sample focus values (first 2 rows):
  - device='pc', device_id='NO_DEVICE_ID', recommend_trace_id=None, device_fingerprint=None
  - device='pc', device_id='NO_DEVICE_ID', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_novel_like_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_novel_like_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/1135 (0.0%)
  - device_id empty=0/1135 (0.0%)
  - recommend_trace_id empty=1135/1135 (100.0%)
  - device_fingerprint empty=1134/1135 (99.9%)
- sample focus values (first 2 rows):
  - device='android', device_id='72488aa444c55f84be697779eb4f35dd', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='1c124146cace78a20c53dfb9f84d8ffe', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_novel_comment_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_novel_comment_d`
- Paimon cols: 25; manifest cols: 25
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['recommend_trace_id', 'device_fingerprint']`
- focus partition empty rates:
  - device empty=0/16 (0.0%)
  - device_id empty=0/16 (0.0%)
  - recommend_trace_id empty=16/16 (100.0%)
  - device_fingerprint empty=16/16 (100.0%)
- sample focus values (first 2 rows):
  - device='android', device_id='f8bdd3bd42b4bba0415c217607074e85', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='010f4b32705abf61a31fa3c64af73fb5', recommend_trace_id=None, device_fingerprint=None
- interesting always-empty in sample: `['recommend_trace_id', 'device_fingerprint']`

## dwd_novel_purchase_d_r

- status: **FOCUS_EMPTY**
- SR table: `dwd_novel_purchase_d`
- Paimon cols: 28; manifest cols: 28
- missing vs manifest: `-`
- missing vs SR (interesting): `-`
- sample dt/n: `2026-08-22` / 5
- focus all-empty in sample: `['device_fingerprint']`
- focus partial empty in sample: `recommend_trace_id=1/5`
- focus partition empty rates:
  - device empty=0/89 (0.0%)
  - device_id empty=0/89 (0.0%)
  - recommend_trace_id empty=79/89 (88.8%)
  - device_fingerprint empty=20/89 (22.5%)
- sample focus values (first 2 rows):
  - device='android', device_id='0a5c25308baa02ed7178b5c0a5a58c22', recommend_trace_id=None, device_fingerprint=None
  - device='android', device_id='78f8e5fe6bf03946a1e942fba318bb7a', recommend_trace_id='1f20581935460fe1', device_fingerprint=None
- interesting always-empty in sample: `['device_fingerprint']`

