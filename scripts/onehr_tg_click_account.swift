import ApplicationServices
import AppKit
import Foundation

/// Click / activate a Telegram multi-account entry by title (e.g. 又初 / Ethan).
/// Prefer Window-menu AXMenuItem; fallback to any pressable AX element with matching title.
///
/// Usage:
///   onehr_tg_click_account <name>
/// Exit 0 on success.

let want = CommandLine.arguments.dropFirst().first?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
guard !want.isEmpty else {
    fputs("ERROR: usage: onehr_tg_click_account <account-name>\n", stderr)
    exit(1)
}

guard AXIsProcessTrusted() else {
    fputs("ERROR: Accessibility not trusted for this process (System Settings → Privacy → Accessibility)\n", stderr)
    exit(2)
}

func attr(_ el: AXUIElement, _ name: CFString) -> AnyObject? {
    var v: AnyObject?
    AXUIElementCopyAttributeValue(el, name, &v)
    return v
}

func roleOf(_ el: AXUIElement) -> String {
    (attr(el, kAXRoleAttribute as CFString) as? String) ?? ""
}

func titleOf(_ el: AXUIElement) -> String {
    (attr(el, kAXTitleAttribute as CFString) as? String) ?? ""
}

func collectMatches(_ el: AXUIElement, want: String, depth: Int = 0, maxDepth: Int = 14, into: inout [AXUIElement]) {
    if depth > maxDepth { return }
    let t = titleOf(el)
    if t == want || t == "Telegram @ \(want)" {
        into.append(el)
    }
    if let kids = attr(el, kAXChildrenAttribute as CFString) as? [AXUIElement] {
        for c in kids {
            collectMatches(c, want: want, depth: depth + 1, maxDepth: maxDepth, into: &into)
        }
    }
}

func press(_ el: AXUIElement) -> Bool {
    var namesRef: CFArray?
    AXUIElementCopyActionNames(el, &namesRef)
    let names = (namesRef as? [String]) ?? []
    if names.contains(kAXPressAction as String) {
        return AXUIElementPerformAction(el, kAXPressAction as CFString) == .success
    }
    // Some menu items only expose AXPress after parent menu opened; try anyway.
    return AXUIElementPerformAction(el, kAXPressAction as CFString) == .success
}

func openWindowMenu(_ appEl: AXUIElement) -> Bool {
    // Telegram macOS: account list lives under Window menu as AXMenuItem titled 又初 / Ethan
    guard let barObj = attr(appEl, kAXMenuBarAttribute as CFString) else {
        return false
    }
    let bar = unsafeBitCast(barObj, to: AXUIElement.self)
    guard let menus = attr(bar, kAXChildrenAttribute as CFString) as? [AXUIElement] else {
        return false
    }
    for m in menus {
        let t = titleOf(m)
        // English "Window" / Chinese "窗口"
        if t == "Window" || t == "窗口" || t.localizedCaseInsensitiveContains("window") {
            return press(m)
        }
    }
    // Fallback: Apple menu bar index often Window near end; try titles containing 窗口
    for m in menus.reversed() {
        let t = titleOf(m)
        if t.contains("窗口") || t == "Window" {
            return press(m)
        }
    }
    return false
}

let running = NSWorkspace.shared.runningApplications.filter {
    ($0.localizedName ?? "") == "Telegram" || ($0.bundleIdentifier ?? "").contains("Telegram")
}
guard let app = running.first else {
    fputs("ERROR: Telegram is not running\n", stderr)
    exit(3)
}

app.activate(options: [])
usleep(300_000)

let appEl = AXUIElementCreateApplication(app.processIdentifier)

// 1) Open Window menu so account items are hittable
_ = openWindowMenu(appEl)
usleep(400_000)

var matches: [AXUIElement] = []
collectMatches(appEl, want: want, into: &matches)

// Prefer AXMenuItem exact title match
let menuItems = matches.filter { roleOf($0) == (kAXMenuItemRole as String) && titleOf($0) == want }
let candidates = !menuItems.isEmpty ? menuItems : matches

guard let target = candidates.first else {
    fputs("ERROR: account UI not found for '\(want)' (open Settings once so multi-account list is visible)\n", stderr)
    exit(4)
}

if press(target) {
    print("OK clicked account=\(want) role=\(roleOf(target))")
    exit(0)
}

fputs("ERROR: AXPress failed for '\(want)' role=\(roleOf(target))\n", stderr)
exit(5)
