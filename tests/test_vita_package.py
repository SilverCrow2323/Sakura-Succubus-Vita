import importlib.util
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "validate_vita_package.py"
SPEC = importlib.util.spec_from_file_location("validate_vita_package", MODULE)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def png(width=1, height=1):
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


def make_package(root, image_name="bg.png"):
    sce = root / "sce_sys"
    contents = sce / "livearea" / "contents"
    contents.mkdir(parents=True)
    (sce / "param.sfo").write_bytes(b"\x00PSF" + b"\x00" * 32)
    (sce / "icon0.png").write_bytes(png())
    (sce / "pic0.png").write_bytes(png(2, 2))
    (contents / "template.xml").write_text(
        '<?xml version="1.0"?><livearea><livearea-background><image>'
        + image_name
        + '</image></livearea-background><gate><startup-image>startup.png'
        + '</startup-image></gate></livearea>',
        encoding="utf-8",
    )
    (contents / "bg.png").write_bytes(png(640, 480))
    (contents / "startup.png").write_bytes(png(640, 480))


def test_checked_in_vita_package_is_structurally_valid():
    result = validator.validate_package(ROOT)
    assert result["status"] == "ok"
    assert result["livearea_assets"]["image"]["filename"] == "bg.png"
    assert result["livearea_assets"]["startup-image"]["filename"] == "startup.png"


def test_livearea_template_cannot_reference_files_outside_contents(tmp_path):
    make_package(tmp_path, image_name="../outside.png")
    with pytest.raises(validator.PackageValidationError, match="plain filename"):
        validator.validate_package(tmp_path)


def test_validator_rejects_non_psf_param_sfo(tmp_path):
    make_package(tmp_path)
    (tmp_path / "sce_sys" / "param.sfo").write_bytes(b"NOPE")
    with pytest.raises(validator.PackageValidationError, match="PSF signature"):
        validator.validate_package(tmp_path)
