# OneHR 截图勿用 open -W 拉「又初打卡截图.app」

## 现象
辅助功能已开（`com.youchu.onehr-capture` auth=2），`open -W -n -a 又初打卡截图` 仍约 30s 返回且不写 `last_screenshot.path`。

## 根因
shell 型 `CFBundleExecutable` 下，LaunchServices 的 `open -W` 常在真正截图脚本跑完前就返回。

## 做法
`onehr_checkin_auto.py` 改为直接 subprocess 跑：
`/Applications/又初打卡截图.app/Contents/MacOS/YouchuOneHRCapture`
仍走 App bundle TCC；失败再回落 `onehr_telegram_devices_screenshot.sh`。

## 验证
2026-09-03 18:45 直跑 App 二进制：账号往返 OK，校验 `account=又初`，写出 path 文件。
