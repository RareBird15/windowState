# Window State

An NVDA add-on that lets you query the state of the current foreground window.

## The Problem

NVDA doesn't tell you whether a window is maximized, restored, or snapped to a side of the screen when you query the title. This information is useful because:

- Pressing Windows+Up Arrow to maximize a window can instead trigger the Windows 11 snap layout chooser, leaving the window in an unknown state.
- Sighted users can glance at a window to see its size and position. Blind users have no equivalent check without trying to resize and listening to what NVDA says happened.
- JAWS includes this information in its JAWS+T title announcement. NVDA does not.

## What This Add-on Does

1. **NVDA+Shift+T**: Reports the state of the current foreground window. Possible states:
   - Maximized
   - Restored (normal windowed mode)
   - Minimized
   - Docked left, docked right, docked top, docked bottom (half-screen snaps)
   - Top left quarter, top right quarter, bottom left quarter, bottom right quarter
   - Not resizable (for windows like the Desktop that can't be maximized or restored)

2. **Optional: NVDA+T enhancement**: When enabled in settings, pressing NVDA+T will announce the window title followed by the state, e.g. "Firefox, maximized." This matches the JAWS behavior. Pressing NVDA+T twice to spell the title and three times to copy it to the clipboard are not affected.

## Settings

Open NVDA Settings > Window State to configure:

- **Append window state to NVDA+T title announcement**: When checked, NVDA+T includes the window state after the title. Off by default.

All commands can be remapped from NVDA's Input Gestures dialog under the "Window State" category.

## Requirements

- NVDA 2026.1 or later

## Author

Lanie Carmelo-Molinar
https://lanie.work

## License

GPL v2
