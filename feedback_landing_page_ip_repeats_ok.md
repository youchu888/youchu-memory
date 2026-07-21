---
name: Landing page IP repeats are normal
description: landing_page_view/click IP 重复不应被当作 IP 异常，一个用户会多次触发；仍要报 NULL / CF-only / 服务器池 IP。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
落地页相关事件（landing_page_view、landing_page_click）的"IP 重复率高 / 分散度低"不应单独视为异常。

**Why:**
一个用户在同一落地页会重复打开、刷新、点击，单个 IP 被多次计入非常正常；同时落地页经 CDN/渠道后 IP 本身就会集中在有限的出口段。因此对这两个事件，低 IP 分散度 ≠ 数据问题。

**How to apply:**
- 分析 `landing_page_view` / `landing_page_click` 的 IP 异常时，**不以 `distinct_ip/cnt` 低**为独立证据；
- 仍然上报以下异常：
  - `ip` 列为空（NULL / 空字符串）占比非零
  - `ip = 'USER_IP'` 占位值
  - IP 全部落在 Cloudflare / 服务端固定池（如 HX 的 AWS 11 个 IP、JHG 的 Linode 2 个 IP）
  - 单一固定服务端 IP
- 其他事件（user_register、order_paid、coin_consume、app_install 等）仍按原规则使用 IP 分散度作为判据。
