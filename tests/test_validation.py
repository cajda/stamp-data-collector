"""
Tests for input validation logic mirroring action_save_record in stamp_collector.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from stamp_collector import REQUIRED_FIELDS, COUNTRIES, CONDITIONS


def validate_stamp(stamp: dict) -> list[str]:
    """Replicate the validation logic from StampApp.action_save_record."""
    errors = []

    missing = [f for f in REQUIRED_FIELDS if not stamp.get(f)]
    if missing:
        errors.append(f"Missing required fields: {missing}")

    code = stamp.get("code", "")
    if code and not code.isdigit():
        errors.append("Code must be a positive integer")

    perf = stamp.get("perforations", "")
    if perf:
        parts = perf.split("x")
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            errors.append("Perforations must be in NxM format (e.g. 11x14)")

    country = stamp.get("country", "")
    if country and country not in COUNTRIES:
        errors.append(f"Country '{country}' is not in the valid country list")

    condition = stamp.get("condition", "")
    if condition and condition not in CONDITIONS:
        errors.append(f"Condition '{condition}' is not valid")

    return errors


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_stamp():
    return {
        "code": "42",
        "country": "Poland",
        "denomination": "1 zl",
        "condition": "Fine",
        "perforations": "11x14",
        "watermark": "",
        "colors": "red, blue",
        "notes": "",
    }


# ── Required fields ───────────────────────────────────────────────────────────

def test_valid_stamp_passes(valid_stamp):
    assert validate_stamp(valid_stamp) == []


def test_all_required_fields_missing():
    errors = validate_stamp({})
    assert any("Missing required fields" in e for e in errors)


@pytest.mark.parametrize("field", list(REQUIRED_FIELDS))
def test_single_required_field_missing(valid_stamp, field):
    valid_stamp[field] = ""
    errors = validate_stamp(valid_stamp)
    assert any("Missing required fields" in e for e in errors)


# ── Code validation ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("code", ["1", "99", "1000"])
def test_code_valid_integer(valid_stamp, code):
    valid_stamp["code"] = code
    assert validate_stamp(valid_stamp) == []


@pytest.mark.parametrize("code", ["abc", "1.5", "-1", "1x2", " "])
def test_code_invalid_non_integer(valid_stamp, code):
    valid_stamp["code"] = code
    errors = validate_stamp(valid_stamp)
    assert any("Code must be a positive integer" in e for e in errors)


# ── Perforations validation ───────────────────────────────────────────────────

@pytest.mark.parametrize("perf", ["11x14", "12x12", "10x10"])
def test_perforations_valid_format(valid_stamp, perf):
    valid_stamp["perforations"] = perf
    assert validate_stamp(valid_stamp) == []


def test_perforations_empty_is_optional(valid_stamp):
    valid_stamp["perforations"] = ""
    assert validate_stamp(valid_stamp) == []


@pytest.mark.parametrize("perf", ["11 x 14", "11x", "x14", "abc", "11-14", "11x14x15"])
def test_perforations_invalid_format(valid_stamp, perf):
    valid_stamp["perforations"] = perf
    errors = validate_stamp(valid_stamp)
    assert any("Perforations" in e for e in errors)


# ── Country validation ────────────────────────────────────────────────────────

@pytest.mark.parametrize("country", ["Poland", "France", "United States", "Japan"])
def test_country_valid(valid_stamp, country):
    valid_stamp["country"] = country
    assert validate_stamp(valid_stamp) == []


@pytest.mark.parametrize("country", ["Neverland", "Atlantis", "poland", "FRANCE"])
def test_country_invalid(valid_stamp, country):
    valid_stamp["country"] = country
    errors = validate_stamp(valid_stamp)
    assert any("not in the valid country list" in e for e in errors)


# ── Condition validation ──────────────────────────────────────────────────────

@pytest.mark.parametrize("condition", list(CONDITIONS))
def test_condition_all_valid_values(valid_stamp, condition):
    valid_stamp["condition"] = condition
    assert validate_stamp(valid_stamp) == []


@pytest.mark.parametrize("condition", ["Perfect", "NM", "fine", "USED"])
def test_condition_invalid(valid_stamp, condition):
    valid_stamp["condition"] = condition
    errors = validate_stamp(valid_stamp)
    assert any("Condition" in e for e in errors)
