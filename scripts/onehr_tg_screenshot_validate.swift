import AppKit
import Foundation
import Vision

/// 校验 OneHR 用的 Telegram「设置 → 设备管理」整页截图。
/// 拒绝：聊天壁纸、风景图、以及「左聊天 + 右设备页」overlay 态。
/// 用法: onehr_tg_screenshot_validate <png路径>
/// 成功 stdout: OK <reason>；失败 stderr + exit 2

let path = CommandLine.arguments.dropFirst().first
guard let path, !path.isEmpty else {
    fputs("ERROR: usage: onehr_tg_screenshot_validate <png>\n", stderr)
    exit(1)
}

let fileURL = URL(fileURLWithPath: path)
guard FileManager.default.fileExists(atPath: path) else {
    fputs("ERROR: file not found: \(path)\n", stderr)
    exit(1)
}

let attrs = try? FileManager.default.attributesOfItem(atPath: path)
let byteSize = (attrs?[.size] as? NSNumber)?.intValue ?? 0
if byteSize > 2_500_000 {
    fputs("FAIL: file too large (\(byteSize) bytes) — likely photo wallpaper, not devices UI\n", stderr)
    exit(2)
}
if byteSize < 20_000 {
    fputs("FAIL: file too small (\(byteSize) bytes)\n", stderr)
    exit(2)
}

guard let image = NSImage(contentsOf: fileURL),
      let tiff = image.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff),
      let cgImage = rep.cgImage else {
    fputs("ERROR: cannot load image\n", stderr)
    exit(1)
}

var ocrText = ""
let request = VNRecognizeTextRequest { request, _ in
    let observations = (request.results as? [VNRecognizedTextObservation]) ?? []
    ocrText = observations
        .compactMap { $0.topCandidates(1).first?.string }
        .joined(separator: " ")
}
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.recognitionLevel = .fast
request.usesLanguageCorrection = false

do {
    try VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
} catch {
    fputs("ERROR: OCR failed: \(error)\n", stderr)
    exit(1)
}

let lower = ocrText.lowercased()

// 左栏必须是「设置」侧栏，不能仍是聊天列表
let settingsSidebarHints = [
    "设置", "设备管理", "隐私与安全", "通用", "我的资料", "通知与声音", "数据与存储",
    "settings", "privacy and security", "notifications",
]
let hasSettingsSidebar = settingsSidebarHints.contains {
    ocrText.localizedCaseInsensitiveContains($0) || lower.contains($0.lowercased())
}

let chatSidebarHints = ["聊天", "chats", "搜索", "search"]
let hasChatSidebar = chatSidebarHints.contains {
    ocrText.localizedCaseInsensitiveContains($0) || lower.contains($0.lowercased())
}

if hasChatSidebar && !hasSettingsSidebar {
    fputs(
        "FAIL: left sidebar is chat list, not Settings (need 设置/设备管理 sidebar)\n",
        stderr
    )
    exit(2)
}

if !hasSettingsSidebar {
    fputs("FAIL: missing Settings sidebar markers (设置/设备管理/隐私与安全…)\n", stderr)
    exit(2)
}

let devicePageHints = [
    "设备管理", "登录设备", "当前设备", "强制注销", "闲置时限",
    "device management", "this device", "current device", "force logout", "inactivity",
]
if devicePageHints.contains(where: { ocrText.localizedCaseInsensitiveContains($0) || lower.contains($0) }) {
    print("OK settings_sidebar+device_page bytes=\(byteSize) ocr_len=\(ocrText.count)")
    exit(0)
}

let snip = String(ocrText.prefix(120)).replacingOccurrences(of: "\n", with: " ")
fputs(
    "FAIL: settings sidebar ok but missing device page content snip=\(snip)\n",
    stderr
)
exit(2)
