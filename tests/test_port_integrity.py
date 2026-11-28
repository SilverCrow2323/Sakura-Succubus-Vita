"""Offline integrity checks for this Vita port's tracked package metadata."""
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCE_SYS = ROOT / "sce_sys"
EXPECTED_TITLE_ID = "RNPYSS001"


def read_sfo(path: Path) -> dict[str, str]:
    raw = path.read_bytes()
    if len(raw) < 20 or raw[:4] != b"\x00PSF":
        raise ValueError("not a valid SFO header")
    key_offset, data_offset, count = struct.unpack_from("<III", raw, 8)
    if count > 256 or 20 + count * 16 > len(raw):
        raise ValueError("invalid SFO index table")
    values: dict[str, str] = {}
    for index in range(count):
        entry = 20 + index * 16
        key_rel, fmt, length, max_length, data_rel = struct.unpack_from("<HHIII", raw, entry)
        key_pos = key_offset + key_rel
        data_pos = data_offset + data_rel
        if key_pos >= len(raw) or data_pos + length > len(raw) or length > max_length:
            raise ValueError("SFO entry is outside the file bounds")
        key_end = raw.find(b"\x00", key_pos)
        if key_end < 0:
            raise ValueError("unterminated SFO key")
        key = raw[key_pos:key_end].decode("utf-8")
        payload = raw[data_pos:data_pos + length].split(b"\x00", 1)[0]
        if fmt == 0x0204:
            values[key] = payload.decode("utf-8")
        else:
            values[key] = payload.hex()
    return values


class VitaPortIntegrityTests(unittest.TestCase):
    def test_sfo_identity_matches_the_published_title_id(self):
        metadata = read_sfo(SCE_SYS / "param.sfo")
        self.assertEqual(metadata.get("TITLE_ID"), EXPECTED_TITLE_ID)
        self.assertEqual(metadata.get("CATEGORY"), "gd")
        self.assertTrue(metadata.get("TITLE", "").strip())
        self.assertTrue(metadata.get("APP_VER", "").strip())

    def test_livearea_assets_are_present_and_well_formed(self):
        for relative in ("icon0.png", "pic0.png", "livearea/contents/bg.png", "livearea/contents/startup.png"):
            data = (SCE_SYS / relative).read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), relative)
        ET.parse(SCE_SYS / "livearea/contents/template.xml")

    def test_original_game_payload_is_not_redistributed(self):
        candidates = [ROOT / "game", ROOT / "PSVITA Port" / "game"]
        self.assertFalse(any(path.exists() for path in candidates))


if __name__ == "__main__":
    unittest.main()
