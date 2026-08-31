import CoreGraphics
import Foundation

let ownerWanted = CommandLine.arguments.dropFirst().first ?? "Telegram"
let opts = CGWindowListOption.optionOnScreenOnly.union(.excludeDesktopElements)
guard let raw = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]] else {
    fputs("ERROR: CGWindowListCopyWindowInfo failed\n", stderr)
    exit(1)
}

var bestWid = 0
var bestX = 0
var bestY = 0
var bestW = 0
var bestH = 0
var bestArea = 0.0

for w in raw {
    let owner = w[kCGWindowOwnerName as String] as? String ?? ""
    if owner != ownerWanted { continue }
    let layer = (w[kCGWindowLayer as String] as? NSNumber)?.intValue ?? -1
    if layer != 0 { continue }
    guard let bounds = w[kCGWindowBounds as String] as? [String: Any] else { continue }
    let width = (bounds["Width"] as? NSNumber)?.doubleValue ?? 0
    let height = (bounds["Height"] as? NSNumber)?.doubleValue ?? 0
    let area = width * height
    if area <= bestArea { continue }
    bestArea = area
    bestWid = (w[kCGWindowNumber as String] as? NSNumber)?.intValue ?? 0
    bestX = Int(((bounds["X"] as? NSNumber)?.doubleValue ?? 0).rounded())
    bestY = Int(((bounds["Y"] as? NSNumber)?.doubleValue ?? 0).rounded())
    bestW = Int(width.rounded())
    bestH = Int(height.rounded())
}

if bestArea <= 0 || bestWid == 0 {
    fputs("ERROR: no on-screen window for \(ownerWanted)\n", stderr)
    exit(2)
}

print("\(bestWid)\t\(bestX),\(bestY)|\(bestW),\(bestH)")
