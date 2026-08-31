import AppKit
import Foundation
import Vision

/// 校验 OneHR 用的 Telegram「设备管理」截图：拒绝聊天壁纸/风景图等非设备页。
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
// 设备页 UI 截图通常 <2MB；今晚错误风景图约 7MB
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
let strongHints = [
    "设备管理", "登录设备", "当前设备", "强制注销", "闲置时限",
    "device management", "this device", "current device", "force logout", "inactivity",
]
if strongHints.contains(where: { ocrText.localizedCaseInsensitiveContains($0) || lower.contains($0) }) {
    print("OK strong_hint bytes=\(byteSize) ocr_len=\(ocrText.count)")
    exit(0)
}

var markers = 0
let soft = ["telegram", "macbook", "iphone", "windows", "app_store", "macos", "android", "desktop"]
for token in soft where lower.contains(token) {
    markers += 1
}
// 设备列表页通常能扫出多个客户端/机型词；壁纸几乎扫不出
if markers >= 2 && ocrText.count >= 40 {
    print("OK soft_markers=\(markers) bytes=\(byteSize) ocr_len=\(ocrText.count)")
    exit(0)
}

let snip = String(ocrText.prefix(120)).replacingOccurrences(of: "\n", with: " ")
fputs(
    "FAIL: not devices page markers=\(markers) ocr_len=\(ocrText.count) snip=\(snip)\n",
    stderr
)
exit(2)
