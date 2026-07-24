#!/usr/bin/env python3
"""Package windowState NVDA add-on into a .nvda-addon file."""

import zipfile
import os

ADDON_NAME = "windowState"
VERSION = "1.0.0"
OUTPUT_FILE = f"{ADDON_NAME}-{VERSION}.nvda-addon"

files = [
	("manifest.ini", "manifest.ini"),
	("LICENSE", "LICENSE"),
	("globalPlugins/windowState.py", "globalPlugins/windowState.py"),
]

# Verify all files exist before building
base = os.path.dirname(os.path.abspath(__file__))
for src, _ in files:
	full = os.path.join(base, src)
	if not os.path.isfile(full):
		print(f"ERROR: Missing file: {src}")
		exit(1)

# Build the zip
output_path = os.path.join(base, OUTPUT_FILE)
with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
	for src, arcname in files:
		full = os.path.join(base, src)
		z.write(full, arcname)
		print(f"  Added: {arcname}")

# Verify: no directory entries
with zipfile.ZipFile(output_path, "r") as z:
	for info in z.infolist():
		assert not info.is_dir(), f"Directory entry found: {info.filename}"
	print(f"\nVerification: {len(z.infolist())} files, no directory entries.")

print(f"\nBuilt: {output_path}")
print(f"Size: {os.path.getsize(output_path)} bytes")