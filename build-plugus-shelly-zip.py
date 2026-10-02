#!/usr/bin/env python3
"""Wrap an ESPHome app image in the official PlugUS 1.7.5 OTA package layout."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


OFFICIAL = Path(__file__).with_name("Shelly-Plus-Plug-US-1.7.5.zip")
APP_SLOT_SIZE = 0x190000


def build(app_path: Path, output_path: Path) -> None:
    if output_path.resolve() in (OFFICIAL.resolve(), app_path.resolve()):
        raise ValueError("Output must not overwrite an input file")
    app = app_path.read_bytes()
    if len(app) < 24 or app[0] != 0xE9:
        raise ValueError("Expected an ESP32 app image beginning with ESP image magic 0xE9")
    if len(app) > APP_SLOT_SIZE:
        raise ValueError(f"App image is {len(app)} bytes; app slot is {APP_SLOT_SIZE} bytes")
    with zipfile.ZipFile(OFFICIAL) as original:
        manifest = json.loads(original.read("manifest.json"))
        if (manifest["name"], manifest["version"]) != ("PlugUS", "1.7.5"):
            raise ValueError("Official package is not PlugUS 1.7.5")
        manifest["parts"]["app"]["size"] = len(app)
        manifest["parts"]["app"]["cs_sha256"] = hashlib.sha256(app).hexdigest()
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_STORED) as result:
            for name in original.namelist():
                data = json.dumps(manifest, separators=(",", ":")).encode() if name == "manifest.json" else app if name == "PlugUS.bin" else original.read(name)
                result.writestr(name, data)

    with zipfile.ZipFile(output_path) as result:
        assert result.read("PlugUS.bin") == app
        assert json.loads(result.read("manifest.json"))["parts"]["app"]["cs_sha256"] == hashlib.sha256(app).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", type=Path, help="ESPHome OTA-format app binary")
    parser.add_argument("output", type=Path, help="Candidate Shelly-format ZIP path")
    args = parser.parse_args()
    build(args.app, args.output)
