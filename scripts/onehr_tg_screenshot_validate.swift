import AppKit
import Foundation
import Vision

/// 校验 OneHR 用的 Telegram「设置 → 设备管理」整页截图。
/// 拒绝：聊天壁纸、风景图、以及「左聊天 + 右设备页」overlay 态。
/// 用法: onehr_tg_screenshot_validate <png路径>

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
    fputs("FAIL: file too large (\(byteSize) bytes) — likely photo wallpaper\n", stderr)
    exit(2)
}
if byteSize < 20_000 {
    fputs("FAIL: file too small (\(byteSize) bytes)\n", stderr)
    exit(2)
}

guard let image = NSImage(contentsOf: fileURL),
      let tiff = image.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff),
      let fullCg = rep.cgImage else {
    fputs("ERROR: cannot load image\n", stderr)
    exit(1)
}

func ocr(_ cgImage: CGImage, accurate: Bool) -> String {
    var text = ""
    let request = VNRecognizeTextRequest { request, _ in
        let observations = (request.results as? [VNRecognizedTextObservation]) ?? []
        text = observations
            .compactMap { $0.topCandidates(1).first?.string }
            .joined(separator: " ")
    }
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.recognitionLevel = accurate ? .accurate : .fast
    request.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
    return text
}

func leftSidebarCrop(_ cg: CGImage, ratio: CGFloat = 0.38) -> CGImage? {
    let w = CGFloat(cg.width)
    let h = CGFloat(cg.height)
    let cropW = max(120, w * ratio)
    return cg.cropping(to: CGRect(x: 0, y: 0, width: cropW, height: h))
}

func rightPanelCrop(_ cg: CGImage, leftRatio: CGFloat = 0.35) -> CGImage? {
    let w = CGFloat(cg.width)
    let h = CGFloat(cg.height)
    let leftW = w * leftRatio
    return cg.cropping(to: CGRect(x: leftW, y: 0, width: w - leftW, height: h))
}

guard let sidebarCg = leftSidebarCrop(fullCg),
      let deviceCg = rightPanelCrop(fullCg) else {
    fputs("ERROR: crop failed\n", stderr)
    exit(1)
}

let sidebarText = ocr(sidebarCg, accurate: true)
let deviceText = ocr(deviceCg, accurate: true)
let sidebarLower = sidebarText.lowercased()
let deviceLower = deviceText.lowercased()

let settingsSidebarHints = [
    "设置", "设备管理", "隐私与安全", "通用", "通知与声音", "数据与存储", "我的资料", "编辑",
    "settings", "privacy and security", "notifications", "data and storage",
]
let settingsHits = settingsSidebarHints.filter {
    sidebarText.localizedCaseInsensitiveContains($0) || sidebarLower.contains($0.lowercased())
}

let chatSidebarHints = ["聊天", "chats", "搜索", "search"]
let chatHits = chatSidebarHints.filter {
    sidebarText.localizedCaseInsensitiveContains($0) || sidebarLower.contains($0.lowercased())
}

if !chatHits.isEmpty && settingsHits.count < 2 {
    fputs(
        "FAIL: left sidebar is chat list (chat=\(chatHits.joined(separator: ",")) settings=\(settingsHits.count))\n",
        stderr
    )
    exit(2)
}

if settingsHits.count < 2 {
    fputs(
        "FAIL: missing Settings sidebar (hits=\(settingsHits.joined(separator: ",")) sidebar_ocr_len=\(sidebarText.count))\n",
        stderr
    )
    exit(2)
}

// 必须是主号「又初」，避免账号往返后停在 Ethan
let primaryHints = ["又初", "youchu8888", "@youchu"]
let hasPrimary = primaryHints.contains {
    sidebarText.localizedCaseInsensitiveContains($0) || sidebarLower.contains($0.lowercased())
}
let ethanOnly = sidebarText.localizedCaseInsensitiveContains("Ethan")
    && !sidebarText.contains("又初")
    && !sidebarLower.contains("youchu")
if ethanOnly || !hasPrimary {
    fputs(
        "FAIL: not primary account 又初 (hasPrimary=\(hasPrimary) ethanOnly=\(ethanOnly))\n",
        stderr
    )
    exit(2)
}

let devicePageHints = [
    "登录设备", "当前设备", "强制注销", "闲置时限", "其他设备",
    "device management", "current device", "force logout", "inactivity",
]
let deviceHits = devicePageHints.filter {
    deviceText.localizedCaseInsensitiveContains($0) || deviceLower.contains($0.lowercased())
}

if deviceHits.isEmpty {
    let snip = String(deviceText.prefix(120)).replacingOccurrences(of: "\n", with: " ")
    fputs("FAIL: missing device page content snip=\(snip)\n", stderr)
    exit(2)
}

print(
    "OK account=又初 settings=\(settingsHits.prefix(3).joined(separator: ",")) device=\(deviceHits.prefix(2).joined(separator: ",")) bytes=\(byteSize)"
)
exit(0)
