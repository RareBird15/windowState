# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries, SpeechDictionaries

# Since some strings in `addon_info` are translatable,
# we need to include them in the .po files.
# Gettext recognizes only strings given as parameters to the `_` function.
# To avoid initializing translations in this module we simply import a "fake" `_` function
# which returns whatever is given to it as an argument.
from site_scons.site_tools.NVDATool.utils import _


# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="windowState",
	# Add-on summary/title, usually the user visible name of the add-on
	# Translators: Summary/title for this add-on
	# to be shown on installation and add-on information found in add-on store
	addon_summary=_("Window State"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-on store
	addon_description=_("""Adds a command to announce the state of the current foreground window (maximized, restored, minimized, or snapped to a side or quarter of the screen). Optionally appends the window state to NVDA+T like JAWS does. Helps blind users confirm whether a window is maximized without triggering the Windows snap layout chooser."""),
	# version
	addon_version="1.1.0",
	# Brief changelog for this version
	# Translators: what's new content for the add-on version to be shown in the add-on store
	addon_changelog=_("""Adopted the NVDA add-on template for standardized builds and CI.
Manifest URL now points to the GitHub repository."""),
	# Author(s)
	addon_author="Lanie Carmelo-Molinar <lanie@lanie.work>",
	# URL for the add-on documentation support
	addon_url="https://github.com/RareBird15/windowState",
	# URL for the add-on repository where the source code can be found
	addon_sourceURL="https://github.com/RareBird15/windowState",
	# Documentation file name
	addon_docFileName="readme.html",
	# Minimum NVDA version supported
	addon_minimumNVDAVersion="2026.1",
	# Last NVDA version supported/tested
	addon_lastTestedNVDAVersion="2026.1",
	# Add-on update channel (default is None, denoting stable releases)
	addon_updateChannel=None,
	# Add-on license such as GPL 2
	addon_license="GPL v2",
	# URL for the license document the add-on is licensed under
	addon_licenseURL=None,
)

# Define the python files that are the sources of your add-on.
# You can either list every file (using "/" ) as a path separator,
# or use glob expressions.
pythonSources: list[str] = ["addon/globalPlugins/*.py"]

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles: list[str] = []

# Base language for the NVDA add-on
baseLanguage: str = "en"

# Markdown extensions for add-on documentation
markdownExtensions: list[str] = []

# Custom braille translation tables
brailleTables: BrailleTables = {}

# Custom speech symbol dictionaries
symbolDictionaries: SymbolDictionaries = {}

# Custom speech dictionaries (distinct from symbol dictionaries above)
speechDictionaries: SpeechDictionaries = {}
