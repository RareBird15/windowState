# WindowState - NVDA add-on to announce and query foreground window state
# Author: Lanie Carmelo-Molinar <lanie@lanie.work>
# License: GPL v2
#
# Adds a command (NVDA+shift+t) to announce the state of the current
# foreground window: maximized, restored, minimized, or snapped to a
# side, half, or quarter of the screen. Optionally appends the window
# state to NVDA+T (the title announcement command) like JAWS does.
#
# The technical approach:
# - Uses winUser.getForegroundWindow() to get the active window handle
# - Uses win32 API calls (IsZoomed, IsIconic, GetWindowPlacement) for
#   basic maximized/minimized/restored detection
# - For snap detection, compares the window's actual rect against the
#   monitor's work area to determine if the window occupies a half or
#   quarter of the screen
#
# v1.0.0: Initial release.
# v1.0.1: Aligned code style with NVDA conventions, added email to manifest.

import globalPluginHandler
import scriptHandler
from scriptHandler import script
import ui
import config
import gui
import gui.settingsDialogs
import wx
import api
import winUser
import speech
from ctypes import Structure, windll, byref, sizeof
from ctypes.wintypes import DWORD, POINT, RECT, UINT
from utils.security import objectBelowLockScreenAndWindowsIsLocked

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIG_KEY = "windowState"

# Window placement flags from winuser.h
SW_SHOWMAXIMIZED = 3
SW_SHOWMINIMIZED = 2
SW_SHOWNORMAL = 1

# Translators: spoken when window is maximized
MSG_MAXIMIZED = _("maximized")
# Translators: spoken when window is restored (normal windowed mode)
MSG_RESTORED = _("restored")
# Translators: spoken when window is minimized
MSG_MINIMIZED = _("minimized")
# Translators: spoken when window is docked to the left half
MSG_DOCKED_LEFT = _("docked left")
# Translators: spoken when window is docked to the right half
MSG_DOCKED_RIGHT = _("docked right")
# Translators: spoken when window is docked to the top half
MSG_DOCKED_TOP = _("docked top")
# Translators: spoken when window is docked to the bottom half
MSG_DOCKED_BOTTOM = _("docked bottom")
# Translators: spoken when window is in the top-left quarter
MSG_TOP_LEFT = _("top left quarter")
# Translators: spoken when window is in the top-right quarter
MSG_TOP_RIGHT = _("top right quarter")
# Translators: spoken when window is in the bottom-left quarter
MSG_BOTTOM_LEFT = _("bottom left quarter")
# Translators: spoken when window is in the bottom-right quarter
MSG_BOTTOM_RIGHT = _("bottom right quarter")
# Translators: spoken when window state cannot be determined
MSG_UNKNOWN = _("unknown window state")


# ---------------------------------------------------------------------------
# Win32 structures and functions for window placement and monitor info
# ---------------------------------------------------------------------------


class WINDOWPLACEMENT(Structure):
	"""Win32 WINDOWPLACEMENT structure.
	Not available in ctypes.wintypes, so we define it ourselves.
	"""

	_fields_ = [
		("length", UINT),
		("flags", UINT),
		("showCmd", UINT),
		("ptMinPosition", POINT),
		("ptMaxPosition", POINT),
		("rcNormalPosition", RECT),
	]

	def __init__(self):
		super().__init__()
		self.length = sizeof(WINDOWPLACEMENT)


class MONITORINFO(Structure):
	"""Win32 MONITORINFO structure for monitor work area."""

	_fields_ = [
		("cbSize", DWORD),
		("rcMonitor", RECT),
		("rcWork", RECT),
		("dwFlags", DWORD),
	]

	def __init__(self):
		super().__init__()
		self.cbSize = sizeof(MONITORINFO)


def getWindowPlacement(hwnd: int) -> int | None:
	"""Get WINDOWPLACEMENT for a window handle.
	Returns the showCmd value (1=normal, 2=minimized, 3=maximized) or None on failure.
	"""
	try:
		placement = WINDOWPLACEMENT()
		if windll.user32.GetWindowPlacement(hwnd, byref(placement)):
			return placement.showCmd
	except Exception:
		pass
	return None


def getWindowRect(hwnd: int) -> tuple[int, int, int, int] | None:
	"""Get the bounding rectangle of a window.
	Returns (left, top, right, bottom) or None on failure.
	"""
	try:
		rect = RECT()
		if windll.user32.GetWindowRect(hwnd, byref(rect)):
			return (rect.left, rect.top, rect.right, rect.bottom)
	except Exception:
		pass
	return None


def getMonitorInfo(hwnd: int) -> tuple[int, int, int, int] | None:
	"""Get the work area of the monitor that contains the given window.
	The work area excludes the taskbar.
	Returns (left, top, right, bottom) of the work area or None on failure.
	"""
	try:
		monitor = windll.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
		if not monitor:
			return None

		info = MONITORINFO()
		if windll.user32.GetMonitorInfoW(monitor, byref(info)):
			work = info.rcWork
			return (work.left, work.top, work.right, work.bottom)
	except Exception:
		pass
	return None


def detectSnapState(
	hwnd: int,
	workArea: tuple[int, int, int, int],
	windowRect: tuple[int, int, int, int],
) -> str | None:
	"""Detect if a window is snapped to a half or quarter of the screen.

	Compares the window's actual rect against the monitor's work area.
	Uses a tolerance threshold (in pixels) to account for window borders
	and slight differences in how Windows positions snapped windows.

	Returns a state string (one of the MSG_ constants) or None if the
	window doesn't appear to be snapped to a specific position.
	"""
	if not workArea or not windowRect:
		return None

	wl, wt, wr, wb = workArea
	wl, wt, wr, wb = int(wl), int(wt), int(wr), int(wb)

	win_l, win_t, win_r, win_b = windowRect
	win_l, win_t, win_r, win_b = int(win_l), int(win_t), int(win_r), int(win_b)

	workWidth = wr - wl
	workHeight = wb - wt

	# Tolerance for border/frame differences (pixels)
	tol = max(15, workWidth // 50)

	# Check if the window fills the full width
	fullWidth = abs((win_r - win_l) - workWidth) <= tol
	# Check if the window fills the full height
	fullHeight = abs((win_b - win_t) - workHeight) <= tol

	if fullWidth and fullHeight:
		# Window fills the entire work area - this is maximized, not snapped
		return None

	halfWidth = abs((win_r - win_l) - (workWidth // 2)) <= tol
	halfHeight = abs((win_b - win_t) - (workHeight // 2)) <= tol

	atLeft = abs(win_l - wl) <= tol
	atRight = abs(win_r - wr) <= tol
	atTop = abs(win_t - wt) <= tol
	atBottom = abs(win_b - wb) <= tol

	# Half-screen snaps
	if halfWidth and fullHeight:
		if atLeft:
			return MSG_DOCKED_LEFT
		if atRight:
			return MSG_DOCKED_RIGHT
	if halfHeight and fullWidth:
		if atTop:
			return MSG_DOCKED_TOP
		if atBottom:
			return MSG_DOCKED_BOTTOM

	# Quarter-screen snaps
	if halfWidth and halfHeight:
		if atLeft and atTop:
			return MSG_TOP_LEFT
		if atRight and atTop:
			return MSG_TOP_RIGHT
		if atLeft and atBottom:
			return MSG_BOTTOM_LEFT
		if atRight and atBottom:
			return MSG_BOTTOM_RIGHT

	return None


def getWindowStateText(hwnd: int | None = None) -> str:
	"""Determine the state of a window and return a human-readable string.

	Args:
		hwnd: Window handle. If None, uses the current foreground window.

	Returns:
		A translated string describing the window state.
	"""
	if hwnd is None:
		hwnd = winUser.getForegroundWindow()
	if not hwnd:
		return MSG_UNKNOWN

	# Check minimized first - minimized windows have showCmd == SW_SHOWMINIMIZED
	showCmd = getWindowPlacement(hwnd)
	if showCmd is not None:
		if showCmd == SW_SHOWMINIMIZED:
			return MSG_MINIMIZED
		if showCmd == SW_SHOWMAXIMIZED:
			return MSG_MAXIMIZED

	# If not maximized or minimized, check for snap positions
	windowRect = getWindowRect(hwnd)
	workArea = getMonitorInfo(hwnd)
	if windowRect and workArea:
		snap = detectSnapState(hwnd, workArea, windowRect)
		if snap:
			return snap

	# If we get here, the window is in normal/restored state
	if showCmd is not None:
		return MSG_RESTORED

	# Fallback: try IsZoomed/IsIconic directly
	try:
		if windll.user32.IsIconic(hwnd):
			return MSG_MINIMIZED
		if windll.user32.IsZoomed(hwnd):
			return MSG_MAXIMIZED
	except Exception:
		pass

	return MSG_RESTORED


# ---------------------------------------------------------------------------
# Settings panel
# ---------------------------------------------------------------------------


class SettingsPanel(gui.settingsDialogs.SettingsPanel):
	title = _("Window State")
	_plugin = None

	def makeSettings(self, sizer):
		settings = config.conf[CONFIG_KEY]

		self._appendToTitleCheckbox = wx.CheckBox(
			self,
			label=_("Append window state to NVDA+T title announcement"),
		)
		self._appendToTitleCheckbox.SetValue(
			self._toBool(settings.get("appendToTitle", False)),
		)
		sizer.Add(self._appendToTitleCheckbox, border=10, flag=wx.ALL)

		helpText = wx.StaticText(
			self,
			label=_(
				"When enabled, pressing NVDA+T will announce the window title "
				"followed by the window state (e.g. 'Firefox, maximized'). "
				"This matches the JAWS behavior. Pressing NVDA+T twice to spell "
				"or three times to copy is not affected.",
			),
		)
		helpText.Wrap(500)
		sizer.Add(helpText, border=10, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM)

	def onSave(self):
		settings = config.conf[CONFIG_KEY]
		settings["appendToTitle"] = self._appendToTitleCheckbox.IsChecked()

	@staticmethod
	def _toBool(val, default=False):
		if isinstance(val, bool):
			return val
		if isinstance(val, str):
			return val.lower() in ("true", "1", "yes")
		return default


# ---------------------------------------------------------------------------
# Global plugin
# ---------------------------------------------------------------------------


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Script category for the Input Gestures dialog
	scriptCategory = _("Window State")

	def __init__(self):
		super().__init__()
		# Register the settings panel
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SettingsPanel)
		# Ensure config section exists
		if CONFIG_KEY not in config.conf:
			config.conf[CONFIG_KEY] = {}
		# Set defaults
		if "appendToTitle" not in config.conf[CONFIG_KEY]:
			config.conf[CONFIG_KEY]["appendToTitle"] = False

	def terminate(self):
		# Unregister the settings panel
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SettingsPanel)
		except (ValueError, AttributeError):
			pass

	# -----------------------------------------------------------------------
	# NVDA+Shift+T: Query window state
	# -----------------------------------------------------------------------

	@script(
		description=_(
			# Translators: Input help message for the report window state command.
			"Reports the state of the current foreground window "
			"(maximized, restored, minimized, or snapped to a side or quarter of the screen).",
		),
		category=_("Window State"),
		gesture="kb:NVDA+shift+t",
		speakOnDemand=True,
	)
	def script_reportWindowState(self, gesture):
		stateText = getWindowStateText()
		ui.message(stateText)

	# -----------------------------------------------------------------------
	# NVDA+T: Override title to optionally append window state
	# -----------------------------------------------------------------------

	@script(
		description=_(
			# Translators: Input help message for the report title command (overridden).
			"Reports the title of the current application or foreground window. "
			"If window state reporting is enabled in settings, the state is appended. "
			"If pressed twice, spells the title. "
			"If pressed three times, copies the title to the clipboard.",
		),
		category=_("System focus"),
		gesture="kb:NVDA+t",
		speakOnDemand=True,
	)
	def script_title(self, gesture):
		obj = api.getForegroundObject()
		# This script is available on the lock screen via getSafeScripts, as such
		# ensure the title does not contain secure information
		# before announcing this object
		if objectBelowLockScreenAndWindowsIsLocked(obj):
			ui.message(gui.blockAction.Context.WINDOWS_LOCKED.translatedMessage)
			return
		title = obj.name
		if not isinstance(title, str) or not title or title.isspace():
			title = obj.appModule.appName if obj.appModule else None
		if not isinstance(title, str) or not title or title.isspace():
			# Translators: Reported when there is no title text for current program or window.
			title = _("No title")

		# Get the window state if the setting is enabled
		appendState = False
		try:
			appendState = SettingsPanel._toBool(
				config.conf[CONFIG_KEY].get("appendToTitle", False),
			)
		except (KeyError, AttributeError):
			pass

		stateText = ""
		if appendState:
			hwnd = winUser.getForegroundWindow()
			if hwnd:
				stateText = getWindowStateText(hwnd)

		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 0:
			if stateText:
				ui.message(f"{title}, {stateText}")
			else:
				ui.message(title)
		elif repeatCount == 1:
			# Spell the title only (state not included in spelling)
			speech.speakSpelling(title)
		else:
			# Copy title to clipboard (state not included in copy)
			api.copyToClip(title, notify=True)
