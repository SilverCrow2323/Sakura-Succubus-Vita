#!/usr/bin/env python3
"""Read-only structural validation for a Ren'Py Vita LiveArea package."""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PNG_SIGNATURE = b"\\x89PNG\\r\\n\\x1a\\n"
PSF_SIGNATURE = b"\\x00PSF"
EXPECTED_TITLE_ID = "RNPYSS001"


class PackageValidationError(ValueError):
    """The repository does not contain a structurally valid Vita package."""


def _safe_regular_file(root: Path, path: Path, label: str) -> Path:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise PackageValidationError(f"{label} escapes the package root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise PackageValidationError(f"{label} must not traverse symbolic links: {current}")
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise PackageValidationError(f"{label} is missing or escapes the package root") from exc
    if not resolved.is_file():
        raise PackageValidationError(f"{label} must be a regular file: {path}")
    return resolved


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
        or "\\\\" in name
        or any(ord(char) < 32 or ord(char) == 127 for char in name)
    ):
        raise PackageValidationError(f"{label} must be a plain filename")
    return name


def _read_title_id(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise PackageValidationError(f"cannot read {path}: {exc}") from exc
    if len(data) < 20 or data[:4] != PSF_SIGNATURE:
        raise PackageValidationError(f"invalid PSF signature or truncated header: {path}")

    _version, key_offset, data_offset, count = struct.unpack_from("<IIII", data, 4)
    index_end = 20 + count * 16
    if (
        count == 0
        or count > 4096
        or index_end > len(data)
        or key_offset < index_end
        or key_offset > data_offset
        or data_offset > len(data)
    ):
        raise PackageValidationError("invalid PSF table offsets or entry count")

    title_ids = []
    for index in range(count):
        entry_offset = 20 + index * 16
        key_relative, data_format, data_length, data_max_length, value_relative = struct.unpack_from(
            "<HHIII", data, entry_offset
        )
        key_start = key_offset + key_relative
        if key_start < key_offset or key_start >= data_offset:
            raise PackageValidationError("PSF key offset is outside the key table")
        key_end = data.find(b"\\x00", key_start, data_offset)
        if key_end < 0:
            raise PackageValidationError("PSF key is not NUL-terminated")
        try:
            key = data[key_start:key_end].decode("ascii")
        except UnicodeDecodeError as exc:
            raise PackageValidationError("PSF key is not ASCII") from exc

        value_start = data_offset + value_relative
        value_end = value_start + data_length
        if (
            data_length > data_max_length
            or value_start < data_offset
            or value_end > len(data)
        ):
            raise PackageValidationError(f"PSF value range is invalid for {key}")

        if key == "TITLE_ID":
            if data_format != 0x0204:
                raise PackageValidationError("PSF TITLE_ID must be a string")
            raw = data[value_start:value_end].split(b"\\x00", 1)[0]
            try:
                title_id = raw.decode("ascii")
            except UnicodeDecodeError as exc:
                raise PackageValidationError("PSF TITLE_ID is not ASCII") from exc
            if not re.fullmatch(r"[A-Z0-9]{9}", title_id):
                raise PackageValidationError("PSF TITLE_ID must contain nine uppercase letters or digits")
            title_ids.append(title_id)

    if len(title_ids) != 1:
        raise PackageValidationError("PSF must contain exactly one TITLE_ID")
    return title_ids[0]


def validate_package(
    root: str | Path,
    expected_title_id: str = EXPECTED_TITLE_ID,
) -> dict[str, object]:
    """Validate the repository's one Vita package without modifying it."""
    root_input = Path(root).absolute()
    if root_input.is_symlink():
        raise PackageValidationError("package root must not be a symbolic link")
    root_path = root_input.resolve()
    if not isinstance(expected_title_id, str) or not re.fullmatch(r"[A-Z0-9]{9}", expected_title_id):
        raise PackageValidationError("expected title ID must contain nine uppercase letters or digits")

    manifests = sorted(root_path.rglob("sce_sys/param.sfo"))
    if len(manifests) != 1:
        raise PackageValidationError(
            f"expected exactly one sce_sys/param.sfo, found {len(manifests)}"
        )
    param_sfo = _safe_regular_file(root_path, manifests[0], "param.sfo")
    title_id = _read_title_id(param_sfo)
    if title_id != expected_title_id:
        raise PackageValidationError(
            f"Vita package TITLE_ID mismatch: expected {expected_title_id}, found {title_id}"
        )

    sce_sys = param_sfo.parent
    icon = _safe_regular_file(root_path, sce_sys / "icon0.png", "icon0.png")
    pic = _safe_regular_file(root_path, sce_sys / "pic0.png", "pic0.png")
    icon_size = _png_dimensions(icon)
    pic_size = _png_dimensions(pic)

    contents = sce_sys / "livearea" / "contents"
    template = _safe_regular_file(root_path, contents / "template.xml", "LiveArea template")
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
        asset = _safe_regular_file(root_path, contents / filename, f"LiveArea {wanted} asset")
        references[wanted] = {"filename": filename, "dimensions": _png_dimensions(asset)}

    return {
        "status": "ok",
        "package_root": str(sce_sys),
        "param_sfo": str(param_sfo),
        "title_id": title_id,
        "icon0_dimensions": icon_size,
        "pic0_dimensions": pic_size,
        "livearea_assets": references,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-title-id", default=EXPECTED_TITLE_ID)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(validate_package(args.root, args.expected_title_id), indent=2))
    except PackageValidationError as exc:
        print(f"[vita-package] ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
