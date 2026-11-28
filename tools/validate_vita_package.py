#!/usr/bin/env python3
"""Read-only structural validation for a Ren'Py Vita LiveArea package."""
from __future__ import annotations

import argparse
import json
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PSF_SIGNATURE = b"\x00PSF"


class PackageValidationError(ValueError):
    """The repository does not contain a structurally valid Vita package."""


def _png_dimensions(path: Path) -> tuple[int, int]:
    try:
        header = path.read_bytes()[:24]
    except OSError as exc:
        raise PackageValidationError(f"cannot read {path}: {exc}") from exc
    if len(header) != 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise PackageValidationError(f"invalid PNG header: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        raise PackageValidationError(f"PNG has zero dimensions: {path}")
    return width, height


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _single_filename(value: str, label: str) -> str:
    name = (value or "").strip()
    if (
        not name
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or any(ord(char) < 32 or ord(char) == 127 for char in name)
    ):
        raise PackageValidationError(f"{label} must be a plain filename")
    return name


def validate_package(root: str | Path) -> dict[str, object]:
    """Validate the repository's one Vita package without modifying it."""
    root_path = Path(root).resolve()
    manifests = sorted(root_path.rglob("sce_sys/param.sfo"))
    if len(manifests) != 1:
        raise PackageValidationError(
            f"expected exactly one sce_sys/param.sfo, found {len(manifests)}"
        )
    param_sfo = manifests[0]
    sce_sys = param_sfo.parent
    try:
        signature = param_sfo.read_bytes()[:4]
    except OSError as exc:
        raise PackageValidationError(f"cannot read {param_sfo}: {exc}") from exc
    if signature != PSF_SIGNATURE:
        raise PackageValidationError(f"invalid PSF signature: {param_sfo}")

    icon = sce_sys / "icon0.png"
    pic = sce_sys / "pic0.png"
    icon_size = _png_dimensions(icon)
    pic_size = _png_dimensions(pic)

    contents = sce_sys / "livearea" / "contents"
    template = contents / "template.xml"
    try:
        xml_root = ET.parse(template).getroot()
    except (OSError, ET.ParseError) as exc:
        raise PackageValidationError(f"invalid LiveArea template: {exc}") from exc
    if _local_name(xml_root.tag) != "livearea":
        raise PackageValidationError("LiveArea template root must be <livearea>")

    references = {}
    for wanted in ("image", "startup-image"):
        nodes = [node for node in xml_root.iter() if _local_name(node.tag) == wanted]
        if len(nodes) != 1 or not (nodes[0].text or "").strip():
            raise PackageValidationError(f"LiveArea template needs one {wanted} reference")
        filename = _single_filename(nodes[0].text, wanted)
        asset = contents / filename
        if not asset.is_file():
            raise PackageValidationError(f"LiveArea asset is missing: {filename}")
        references[wanted] = {"filename": filename, "dimensions": _png_dimensions(asset)}

    return {
        "status": "ok",
        "package_root": str(sce_sys),
        "param_sfo": str(param_sfo),
        "icon0_dimensions": icon_size,
        "pic0_dimensions": pic_size,
        "livearea_assets": references,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        print(json.dumps(validate_package(args.root), indent=2))
    except PackageValidationError as exc:
        print(f"[vita-package] ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
