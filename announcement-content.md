# WindowState Announcement Content

## Blog Post

**Status:** Draft at `content/technology/windowstate-nvda-add-on.md` (draft: true)
**URL when published:** https://lanie.work/technology/windowstate-nvda-add-on/

---

## Mastodon Post

New NVDA add-on: WindowState. Press NVDA+Shift+T to hear if your foreground window is maximized, restored, minimized, or snapped to a side or quarter of the screen. Optionally appends the state to NVDA+T like JAWS does.

I built this because pressing Windows+Up Arrow to maximize a window sometimes triggers the Windows 11 snap chooser instead, and NVDA doesn't tell you which one happened. There's no way to just ask "is this window maximized?" without trying to resize and listening to what changed. Now there is.

Requires NVDA 2026.1+. Free and open source.

Download: https://github.com/RareBird15/windowState/releases/tag/v1.0.0

#NVDA #Accessibility #BlindTech #ScreenReader #AssistiveTech

---

## NVDA Add-ons List Email

**To:** nvda-addons@groups.io (or nvda-users@groups.io)
**Subject:** New add-on: WindowState - report foreground window state

Hi everyone,

I've released a new NVDA add-on called WindowState. It fills a gap that JAWS users have but NVDA users don't: the ability to query whether the current window is maximized.

## What it does

1. NVDA+Shift+T reports the state of the current foreground window: maximized, restored, minimized, docked left/right/top/bottom (half-screen snaps), or top-left/top-right/bottom-left/bottom-right (quarter-screen snaps).

2. Optional NVDA+T enhancement: when enabled in Settings > Window State, NVDA+T appends the window state to the title announcement (e.g. "Firefox, maximized"), matching the JAWS behavior. This is off by default. The existing press-twice-to-spell and press-three-times-to-copy behaviors are not affected.

All commands are remappable from the Input Gestures dialog.

## Why I built it

Pressing Windows+Up Arrow to maximize a window can trigger the Windows 11 snap layout chooser instead, leaving the window in an unknown state. NVDA announces window state changes when you press Windows+Arrow keys to resize, but there's no way to query the current state without attempting a resize. Sighted users can glance at a window to check its state. Blind users now have an equivalent.

## Technical details

- Uses GetWindowPlacement for maximized/minimized/restored detection
- Uses GetWindowRect + MonitorFromWindow + GetMonitorInfoW for snap detection (compares window rect against monitor work area with pixel tolerance for borders)
- Requires NVDA 2026.1 or later
- GPL v2, open source

## Download

https://github.com/RareBird15/windowState/releases/tag/v1.0.0

I'd appreciate feedback, especially from anyone using multi-monitor setups or unusual resolutions, since the snap detection logic compares window position against the monitor work area.

Lanie Carmelo-Molinar
https://lanie.work
