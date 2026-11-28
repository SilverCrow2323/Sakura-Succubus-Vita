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
        b"\\x89PNG\\r\\n\\x1a\\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\\x08\\x06\\x00\\x00\\x00"
    )


def psf(title_id):
    key_table = b"TITLE_ID\\x00"
    value = title_id.encode("ascii") + b"\\x00"
    key_offset = 20 + 16
    data_offset = key_offset + len(key_table)
    header = b"\\x00PSF" + struct.pack("<IIII", 0x00000101, key_offset, data_offset, 1)
    entry = struct.pack("<HHIII", 0, 0x0204, len(value), len(value), 0)
    return header + entry + key_table + value


def make_package(root, image_name="bg.png", title_id=validator.EXPECTED_TITLE_ID):
    sce = root / "sce_sys"
    contents = sce / "livearea" / "contents"
    contents.mkdir(parents=True)
    (sce / "param.sfo").write_bytes(psf(title_id))
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


def test_checked_in_vita_package_has_expected_title_id_and_livearea_assets():
    result = validator.validate_package(ROOT)
    assert result["status"] == "ok"
    assert result["title_id"] == "RNPYSS001"
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


def test_validator_rejects_wrong_game_title_id(tmp_path):
    make_package(tmp_path, title_id="ABCDEFGHI")
    with pytest.raises(validator.PackageValidationError, match="TITLE_ID mismatch"):
        validator.validate_package(tmp_path)


def test_validator_rejects_symlinked_livearea_asset(tmp_path):
    make_package(tmp_path)
    contents = tmp_path / "sce_sys" / "livearea" / "contents"
    external = tmp_path / "outside.png"
    external.write_bytes(png(640, 480))
    (contents / "bg.png").unlink()
    (contents / "bg.png").symlink_to(external)

    with pytest.raises(validator.PackageValidationError, match="symbolic links"):
        validator.validate_package(tmp_path)


def test_validator_rejects_symlinked_param_sfo(tmp_path):
    make_package(tmp_path)
    sce = tmp_path / "sce_sys"
    external = tmp_path / "external.sfo"
    external.write_bytes(psf(validator.EXPECTED_TITLE_ID))
    (sce / "param.sfo").unlink()
    (sce / "param.sfo").symlink_to(external)

    with pytest.raises(validator.PackageValidationError, match="symbolic links"):
        validator.validate_package(tmp_path)


def test_validator_rejects_truncated_psf_tables(tmp_path):
    make_package(tmp_path)
    (tmp_path / "sce_sys" / "param.sfo").write_bytes(b"\\x00PSF" + b"\\x00" * 16)

    with pytest.raises(validator.PackageValidationError, match="offsets or entry count"):
        validator.validate_package(tmp_path)
