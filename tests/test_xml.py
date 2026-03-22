"""
Tests for XML file structure: building, loading, and round-trip integrity.
"""
import sys
import os
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from stamp_collector import _build_xml, _load_xml, FIELD_KEYS


@pytest.fixture
def sample_stamps():
    return [
        {
            "code": "1", "country": "Poland", "denomination": "1 zl",
            "condition": "Fine", "perforations": "12x12", "watermark": "100",
            "catalog_type": "Scott (Sn)", "catalog_number": "42",
            "colors": "red, blue", "watermark_image": "", "stamp_image": "",
            "notes": "test note", "created": "2026-01-01 10:00:00",
        },
        {
            "code": "2", "country": "France", "denomination": "5 FF",
            "condition": "Mint NH", "perforations": "", "watermark": "",
            "catalog_type": "", "catalog_number": "",
            "colors": "green", "watermark_image": "", "stamp_image": "",
            "notes": "", "created": "2026-02-15 12:30:00",
        },
    ]


@pytest.fixture
def xml_file(sample_stamps, tmp_path):
    path = tmp_path / "test_stamps.xml"
    path.write_text(_build_xml(sample_stamps), encoding="utf-8")
    return str(path)


# ── Build XML structure ────────────────────────────────────────────────────────

def test_build_xml_is_valid(sample_stamps):
    xml_str = _build_xml(sample_stamps)
    root = ET.fromstring(xml_str)  # raises if invalid XML
    assert root is not None


def test_build_xml_root_tag(sample_stamps):
    xml_str = _build_xml(sample_stamps)
    root = ET.fromstring(xml_str)
    assert root.tag == "stamps"


def test_build_xml_stamp_count(sample_stamps):
    xml_str = _build_xml(sample_stamps)
    root = ET.fromstring(xml_str)
    assert len(root.findall("stamp")) == len(sample_stamps)


def test_build_xml_each_stamp_has_all_fields(sample_stamps):
    xml_str = _build_xml(sample_stamps)
    root = ET.fromstring(xml_str)
    for stamp_elem in root.findall("stamp"):
        found_keys = {child.tag for child in stamp_elem}
        for key in FIELD_KEYS:
            assert key in found_keys, f"Missing field '{key}' in stamp element"


def test_build_xml_field_values(sample_stamps):
    xml_str = _build_xml(sample_stamps)
    root = ET.fromstring(xml_str)
    first = root.findall("stamp")[0]
    assert first.find("code").text == "1"
    assert first.find("country").text == "Poland"
    assert first.find("colors").text == "red, blue"


def test_build_xml_empty_collection():
    xml_str = _build_xml([])
    root = ET.fromstring(xml_str)
    assert root.tag == "stamps"
    assert len(root.findall("stamp")) == 0


# ── Load XML structure ─────────────────────────────────────────────────────────

def test_load_xml_returns_list(xml_file):
    stamps = _load_xml(xml_file)
    assert isinstance(stamps, list)


def test_load_xml_correct_count(xml_file, sample_stamps):
    stamps = _load_xml(xml_file)
    assert len(stamps) == len(sample_stamps)


def test_load_xml_each_stamp_is_dict(xml_file):
    stamps = _load_xml(xml_file)
    for stamp in stamps:
        assert isinstance(stamp, dict)


def test_load_xml_each_stamp_has_all_keys(xml_file):
    stamps = _load_xml(xml_file)
    for stamp in stamps:
        for key in FIELD_KEYS:
            assert key in stamp, f"Key '{key}' missing from loaded stamp"


def test_load_xml_invalid_file_raises(tmp_path):
    bad = tmp_path / "bad.xml"
    bad.write_text("this is not xml", encoding="utf-8")
    with pytest.raises(ET.ParseError):
        _load_xml(str(bad))


def test_load_xml_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        _load_xml("/nonexistent/path/stamps.xml")


# ── Round-trip integrity ───────────────────────────────────────────────────────

def test_roundtrip_preserves_all_fields(sample_stamps, tmp_path):
    path = str(tmp_path / "roundtrip.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_build_xml(sample_stamps))
    loaded = _load_xml(path)
    for original, recovered in zip(sample_stamps, loaded):
        for key in FIELD_KEYS:
            assert recovered[key] == original.get(key, ""), (
                f"Round-trip mismatch on key '{key}'"
            )


def test_roundtrip_empty_collection(tmp_path):
    path = str(tmp_path / "empty.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_build_xml([]))
    loaded = _load_xml(path)
    assert loaded == []
