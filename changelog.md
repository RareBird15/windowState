# Changelog

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
