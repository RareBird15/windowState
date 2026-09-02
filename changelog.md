# Changelog

## v1.3.0

- Added detection of Windows 11 Snap Layout thirds: left third, middle third, right third, left two thirds, and right two thirds.
- Added an optional "Report the display number with the window state" setting. When enabled, the window state is followed by the display number (e.g. "restored, on display 1"), matching JAWS behavior for multiple monitors. Off by default.

## v1.2.0

- The Desktop and other non-resizable windows now report "not resizable" instead of "restored" when queried with NVDA+Shift+T. This matches JAWS behavior for windows that can't be maximized or restored.

## v1.1.0

- Adopted the NVDA add-on template for standardized builds and CI/CD.
- Manifest URL now points to the GitHub repository instead of the personal website.
- Added SCons build system, GitHub Actions CI, Ruff linting, and Pyright type checking.
- No functional changes to the add-on behavior.

## v1.0.1

- Aligned code style with NVDA conventions (camelCase function names, direct imports, type hints).
- Added email to manifest author field.
- Added lock screen security check to the NVDA+T override.

## v1.0.0

- Initial release.
- NVDA+Shift+T reports window state (maximized, restored, minimized, snapped).
- Optional NVDA+T enhancement to append window state to title announcement, matching JAWS behavior.
