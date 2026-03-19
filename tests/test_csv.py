"""
Tests for CSV file structure: headers, row integrity, and export format.
"""
import sys
import os
import csv
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from stamp_collector import FIELD_KEYS


@pytest.fixture
def sample_stamps():
    return [
        {
            "code": "1", "country": "Poland", "denomination": "1 zl",
            "condition": "Fine", "perforations": "11x14", "watermark": "100",
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


def write_csv(stamps: list[dict]) -> str:
    """Write stamps to a CSV string the same way the app does."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELD_KEYS)
    writer.writeheader()
    writer.writerows(stamps)
    return buf.getvalue()


def read_csv(csv_str: str) -> tuple[list[str], list[dict]]:
    """Return (headers, rows) from a CSV string."""
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    return list(reader.fieldnames or []), rows


# ── Header structure ──────────────────────────────────────────────────────────

def test_csv_headers_match_field_keys(sample_stamps):
    csv_str = write_csv(sample_stamps)
    first_line = csv_str.splitlines()[0]
    headers = first_line.split(",")
    assert headers == FIELD_KEYS


def test_csv_has_no_extra_columns(sample_stamps):
    csv_str = write_csv(sample_stamps)
    reader = csv.DictReader(io.StringIO(csv_str))
    list(reader)  # consume rows
    assert list(reader.fieldnames) == FIELD_KEYS


# ── Row structure ─────────────────────────────────────────────────────────────

def test_csv_row_count(sample_stamps):
    csv_str = write_csv(sample_stamps)
    lines = [l for l in csv_str.splitlines() if l.strip()]
    # 1 header + N data rows
    assert len(lines) == len(sample_stamps) + 1


def test_csv_each_row_has_all_columns(sample_stamps):
    csv_str = write_csv(sample_stamps)
    reader = csv.DictReader(io.StringIO(csv_str))
    for row in reader:
        for key in FIELD_KEYS:
            assert key in row, f"Column '{key}' missing from CSV row"


def test_csv_empty_collection():
    csv_str = write_csv([])
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) == 1  # header only
    assert lines[0].split(",") == FIELD_KEYS


# ── Value integrity ───────────────────────────────────────────────────────────

def test_csv_values_match_source(sample_stamps):
    csv_str = write_csv(sample_stamps)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    for original, row in zip(sample_stamps, rows):
        for key in FIELD_KEYS:
            assert row[key] == original.get(key, ""), (
                f"Value mismatch on column '{key}'"
            )


def test_csv_special_characters_preserved(sample_stamps):
    sample_stamps[0]["notes"] = 'note with, comma and "quotes"'
    csv_str = write_csv(sample_stamps)
    reader = csv.DictReader(io.StringIO(csv_str))
    first_row = next(reader)
    assert first_row["notes"] == 'note with, comma and "quotes"'


# ── Reading an existing CSV file ──────────────────────────────────────────────

def test_read_example_csv_headers(tmp_path):
    """A valid CSV file from the examples dir must have all FIELD_KEYS as headers."""
    examples_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples"
    )
    csv_files = [f for f in os.listdir(examples_dir) if f.endswith(".csv")]
    assert csv_files, "No CSV files found in examples/"

    for fname in csv_files:
        path = os.path.join(examples_dir, fname)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
        # All app-core fields (excluding image fields added in v2) must be present
        core_fields = ["code", "country", "denomination", "condition",
                       "perforations", "watermark", "colors", "notes", "created"]
        for field in core_fields:
            assert field in headers, (
                f"'{field}' missing from headers in {fname}"
            )


def test_write_and_read_csv_file(sample_stamps, tmp_path):
    path = tmp_path / "output.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_KEYS)
        writer.writeheader()
        writer.writerows(sample_stamps)

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == len(sample_stamps)
    for original, row in zip(sample_stamps, rows):
        assert row["code"] == original["code"]
        assert row["country"] == original["country"]
        assert row["condition"] == original["condition"]
