# WindowState - NVDA add-on to announce and query foreground window state
# Author: Lanie Carmelo-Molinar
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

import globalPluginHandler
import scriptHandler
import ui
import config
import gui
import gui.settingsDialogs
import wx
import api
import winUser
import winKernel
from ctypes import Structure, wintypes, windll, byref, sizeof

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
		("length", wintypes.UINT),
		("flags", wintypes.UINT),
		("showCmd", wintypes.UINT),
		("ptMinPosition", wintypes.POINT),
		("ptMaxPosition", wintypes.POINT),
		("rcNormalPosition", wintypes.RECT),
	]


class MONITORINFO(Structure):
	"""Win32 MONITORINFO structure for monitor work area."""
	_fields_ = [
		("cbSize", wintypes.DWORD),
		("rcMonitor", wintypes.RECT),
		("rcWork", wintypes.RECT),
		("dwFlags", wintypes.DWORD),
	]


def _get_window_placement(hwnd):
	"""Get WINDOWPLACEMENT for a window handle.
	Returns the showCmd value (1=normal, 2=minimized, 3=maximized) or None on failure.
	"""
	try:
		placement = WINDOWPLACEMENT()
		placement.length = sizeof(WINDOWPLACEMENT)
		if windll.user32.GetWindowPlacement(hwnd, byref(placement)):
			return placement.showCmd
	except Exception:
		pass
	return None


def _get_window_rect(hwnd):
	"""Get the bounding rectangle of a window.
	Returns (left, top, right, bottom) or None on failure.
	"""
	try:
		rect = wintypes.RECT()
		if windll.user32.GetWindowRect(hwnd, byref(rect)):
			return (rect.left, rect.top, rect.right, rect.bottom)
	except Exception:
		pass
	return None


def _get_monitor_info(hwnd):
	"""Get the work area of the monitor that contains the given window.
	The work area excludes the taskbar.
	Returns (left, top, right, bottom) of the work area or None on failure.
	"""
	try:
		monitor = windll.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
		if not monitor:
			return None

		info = MONITORINFO()
		info.cbSize = sizeof(MONITORINFO)
		if windll.user32.GetMonitorInfoW(monitor, byref(info)):
			work = info.rcWork
			return (work.left, work.top, work.right, work.bottom)
	except Exception:
		pass
	return None


def _detect_snap_state(hwnd, work_area, window_rect):
	"""Detect if a window is snapped to a half or quarter of the screen.

	Compares the window's actual rect against the monitor's work area.
	Uses a tolerance threshold (in pixels) to account for window borders
	and slight differences in how Windows positions snapped windows.

	Returns a state string (one of the MSG_ constants) or None if the
	window doesn't appear to be snapped to a specific position.
	"""
	if not work_area or not window_rect:
		return None

	wl, wt, wr, wb = work_area
	wl, wt, wr, wb = int(wl), int(wt), int(wr), int(wb)

	win_l, win_t, win_r, win_b = window_rect
	win_l, win_t, win_r, win_b = int(win_l), int(win_t), int(win_r), int(win_b)

	work_width = wr - wl
	work_height = wb - wt

	# Tolerance for border/frame differences (pixels)
	tol = max(15, work_width // 50)

	# Check if the window fills the full width
	full_width = abs((win_r - win_l) - work_width) <= tol
	# Check if the window fills the full height
	full_height = abs((win_b - win_t) - work_height) <= tol

	if full_width and full_height:
		# Window fills the entire work area - this is maximized, not snapped
		return None

	half_width = abs((win_r - win_l) - (work_width // 2)) <= tol
	half_height = abs((win_b - win_t) - (work_height // 2)) <= tol

	at_left = abs(win_l - wl) <= tol
	at_right = abs(win_r - wr) <= tol
	at_top = abs(win_t - wt) <= tol
	at_bottom = abs(win_b - wb) <= tol

	# Half-screen snaps
	if half_width and full_height:
		if at_left:
			return MSG_DOCKED_LEFT
		if at_right:
			return MSG_DOCKED_RIGHT
	if half_height and full_width:
		if at_top:
			return MSG_DOCKED_TOP
		if at_bottom:
			return MSG_DOCKED_BOTTOM

	# Quarter-screen snaps
	if half_width and half_height:
		if at_left and at_top:
			return MSG_TOP_LEFT
		if at_right and at_top:
			return MSG_TOP_RIGHT
		if at_left and at_bottom:
			return MSG_BOTTOM_LEFT
		if at_right and at_bottom:
			return MSG_BOTTOM_RIGHT

	return None


def get_window_state_text(hwnd=None):
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
	show_cmd = _get_window_placement(hwnd)
	if show_cmd is not None:
		if show_cmd == SW_SHOWMINIMIZED:
			return MSG_MINIMIZED
		if show_cmd == SW_SHOWMAXIMIZED:
			return MSG_MAXIMIZED

	# If not maximized or minimized, check for snap positions
	window_rect = _get_window_rect(hwnd)
	work_area = _get_monitor_info(hwnd)
	if window_rect and work_area:
		snap = _detect_snap_state(hwnd, work_area, window_rect)
		if snap:
			return snap

	# If we get here, the window is in normal/restored state
	if show_cmd is not None:
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
	title = "Window State"
	_plugin = None

	def makeSettings(self, sizer):
		settings = config.conf[CONFIG_KEY]

		self._appendToTitleCheckbox = wx.CheckBox(
			self, label=_("Append window state to NVDA+T title announcement")
		)
		self._appendToTitleCheckbox.SetValue(
			self._to_bool(settings.get("appendToTitle", False))
		)
		sizer.Add(self._appendToTitleCheckbox, border=10, flag=wx.ALL)

		helpText = wx.StaticText(
			self,
			label=_(
				"When enabled, pressing NVDA+T will announce the window title "
				"followed by the window state (e.g. 'Firefox, maximized'). "
				"This matches the JAWS behavior. Pressing NVDA+T twice to spell "
				"or three times to copy is not affected."
			)
		)
		helpText.Wrap(500)
		sizer.Add(helpText, border=10, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM)

	def onSave(self):
		settings = config.conf[CONFIG_KEY]
		settings["appendToTitle"] = self._appendToTitleCheckbox.IsChecked()

	@staticmethod
	def _to_bool(val, default=False):
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

	@scriptHandler.script(
		description=_(
			# Translators: Input help message for the report window state command.
			"Reports the state of the current foreground window "
			"(maximized, restored, minimized, or snapped to a side or quarter of the screen)."
		),
		category=_("Window State"),
		gesture="kb:NVDA+shift+t",
		speakOnDemand=True,
	)
	def script_reportWindowState(self, gesture):
		state_text = get_window_state_text()
		ui.message(state_text)

	# -----------------------------------------------------------------------
	# NVDA+T: Override title to optionally append window state
	# -----------------------------------------------------------------------

	@scriptHandler.script(
		description=_(
			# Translators: Input help message for the report title command (overridden).
			"Reports the title of the current application or foreground window. "
			"If window state reporting is enabled in settings, the state is appended. "
			"If pressed twice, spells the title. "
			"If pressed three times, copies the title to the clipboard."
		),
		category=_("System focus"),
		gesture="kb:NVDA+t",
		speakOnDemand=True,
	)
	def script_title(self, gesture):
		obj = api.getForegroundObject()
		title = obj.name
		if not isinstance(title, str) or not title or title.isspace():
			title = obj.appModule.appName if obj.appModule else None
		if not isinstance(title, str) or not title or title.isspace():
			# Translators: Reported when there is no title text for current program or window.
			title = _("No title")

		# Get the window state if the setting is enabled
		append_state = False
		try:
			append_state = SettingsPanel._to_bool(
				config.conf[CONFIG_KEY].get("appendToTitle", False)
			)
		except (KeyError, AttributeError):
			pass

		state_text = ""
		if append_state:
			hwnd = winUser.getForegroundWindow()
			if hwnd:
				state_text = get_window_state_text(hwnd)

		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 0:
			if state_text:
				ui.message(f"{title}, {state_text}")
			else:
				ui.message(title)
		elif repeatCount == 1:
			# Spell the title only (state not included in spelling)
			import speech
			speech.speakSpelling(title)
		else:
			# Copy title to clipboard (state not included in copy)
			api.copyToClip(title, notify=True)