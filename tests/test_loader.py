"""Tests for combining worker CSVs into the DB-ready frame."""

import pandas as pd
import pytest
from src.config import configscape
from src.loader import combine_files, frame_to_rows

WORKER_COLUMNS = [
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
    "score_wifi",
    "score_paid_wifi",
    "score_breakfast",
    "score_staff",
    "score_services",
    "score_clean",
    "score_comfort",
    "score_value",
    "score_location",
    "score_total",
    "score_accuracy",
    "score_pool",
    "score_walking",
    "url_index",
]


def _worker_row(**overrides):
    row = {
        "booking.env.b_map_center_latitude": "13.75234567",
        "booking.env.b_map_center_longitude": "100.55312345",
        "atnm": "hotel123",
        "hotel_name": "Siam Grand Hotel",
        "city_name": "Bangkok",
        "region_name": "Bangkok",
        "country_name": "Thailand",
        "dest_type": "Hotel",
        "dest_ufi": "9876543",
        "hotel_id": "555123",
        "hotel_currency": "THB",
        "score_wifi": 10.0,
        "score_paid_wifi": "",
        "score_breakfast": 8.5,
        "score_staff": 9.4,
        "score_services": 9.2,
        "score_clean": 9.1,
        "score_comfort": 9.0,
        "score_value": 9.3,
        "score_location": 9.8,
        "score_total": 9.2,
        "score_accuracy": 9.5,
        "score_pool": "",
        "score_walking": 9.7,
        "url_index": 1,
    }
    row.update(overrides)
    return row


@pytest.fixture
def worker_dir(tmp_path):
    first = pd.DataFrame([_worker_row(), _worker_row(), _worker_row(url_index=2, hotel_name="Riverside Inn")])
    first.to_csv(tmp_path / "worker_0-2.csv", index=False)
    second = pd.DataFrame([_worker_row(url_index=2, hotel_name="Riverside Inn")])
    second.to_csv(tmp_path / "worker_2-3.csv", index=False)
    return tmp_path


def test_combine_files_deduplicates_and_renames_columns(worker_dir):
    df = combine_files(worker_dir)
    assert len(df) == 2
    assert list(df.columns) == configscape.order_col
    assert set(df["hotel_name"]) == {"Siam Grand Hotel", "Riverside Inn"}


def test_combine_files_positional_remap(worker_dir):
    df = combine_files(worker_dir)
    # atnm (worker col 3) maps to the DB `type` column; dest_ufi maps to dest_id.
    assert set(df["type"]) == {"hotel123"}
    assert df["dest_id"].dtype.kind == "f"
    assert set(df["dest_id"]) == {9876543.0}


def test_combine_files_keeps_nulls_and_fills_inuse(worker_dir):
    df = combine_files(worker_dir)
    assert (df["inuse"] == 0).all()
    # Missing scores stay NULL instead of being silently filled with 0.
    siam = df[df["hotel_name"] == "Siam Grand Hotel"]
    assert siam["score_paid_wifi"].isna().all()
    assert siam["score_pool"].isna().all()
    assert not siam["score_clean"].isna().all()


def test_combine_files_requires_worker_csvs(tmp_path):
    with pytest.raises(FileNotFoundError):
        combine_files(tmp_path)


def test_frame_to_rows_converts_missing_to_sql_null(worker_dir):
    df = combine_files(worker_dir)
    rows = frame_to_rows(df)
    assert len(rows) == len(df)
    loc_name = df.columns.get_loc("hotel_name")
    loc_dest = df.columns.get_loc("dest_id")
    loc_wifi = df.columns.get_loc("score_paid_wifi")
    siam = next(r for r in rows if r[loc_name] == "Siam Grand Hotel")
    assert siam[loc_dest] == 9876543.0
    assert siam[loc_wifi] is None
