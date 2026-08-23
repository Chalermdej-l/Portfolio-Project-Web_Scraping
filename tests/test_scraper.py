"""Regression tests for the hotel-page parser, pinned to tests/fixtures/hotel.html."""

from pathlib import Path

from src.scraper import parse_hotel

FIXTURE = Path(__file__).parent / "fixtures" / "hotel.html"
CORE_KEYS = {
    "booking.env.b_map_center_latitude",
    "booking.env.b_map_center_longitude",
    "atnm",
    "hotel_name",
    "city_name",
    "region_name",
    "country_name",
    "dest_type",
    "dest_ufi",
    "hotel_id",
    "hotel_currency",
}


def _parse():
    return parse_hotel(FIXTURE.read_bytes())


def test_parse_hotel_extracts_coordinates():
    data = _parse()
    assert data["booking.env.b_map_center_latitude"] == "13.75234567"
    assert data["booking.env.b_map_center_longitude"] == "100.55312345"


def test_parse_hotel_extracts_utag_fields():
    data = _parse()
    assert data["atnm"] == "hotel123"
    assert data["hotel_name"] == "Siam Grand Hotel"
    assert data["city_name"] == "Bangkok"
    assert data["region_name"] == "Bangkok"
    assert data["country_name"] == "Thailand"
    assert data["dest_type"] == "Hotel"
    assert data["dest_ufi"] == "9876543"
    assert data["hotel_id"] == "555123"


def test_parse_hotel_extracts_currency():
    data = _parse()
    assert data["hotel_currency"] == "THB"


def test_parse_hotel_extracts_total_scores_only():
    data = _parse()
    score_keys = set(data) - CORE_KEYS
    # The parser keeps only customerType == TOTAL segments (the "ALL" one is skipped),
    # and the key is sliced from the page JSON, keeping its closing quote.
    assert score_keys == {'Cleanliness"'}
    assert data['Cleanliness"'] == "9.1"
