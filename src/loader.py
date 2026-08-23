"""Step 3: combine the worker CSVs and bulk-load them into SQL Server.

Missing values are kept as NULL in the database (only `inuse` defaults to 0),
and failures propagate instead of returning a sentinel string.
"""

import logging
from pathlib import Path

import pandas as pd
import pyodbc as py

from src.config import configscape

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("Output")


def combine_files(output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    """Concatenate Output/*.csv, de-duplicate, and align columns to the DB contract."""
    frames = [pd.read_csv(file) for file in sorted(output_dir.glob("*.csv"))]
    if not frames:
        raise FileNotFoundError(f"No worker CSVs found in {output_dir}")
    combine_list = pd.concat(frames, ignore_index=True)
    strlist = combine_list.dtypes[combine_list.dtypes == "object"].index
    combine_list = combine_list.drop_duplicates()
    combine_list[strlist] = combine_list[strlist].astype("string")
    combine_list["dest_ufi"] = combine_list["dest_ufi"].astype("float")
    combine_list["inuse"] = 0
    combine_list.columns = configscape.col_name
    combine_list = combine_list[configscape.order_col]
    combine_list["inuse"] = combine_list["inuse"].fillna(0)
    return combine_list


def frame_to_rows(frame: pd.DataFrame) -> list[list]:
    """Rows as plain lists with missing values converted to None (SQL NULL)."""
    rows = frame.astype(object).where(frame.notna(), None)
    return rows.values.tolist()


def load_to_sql(frame: pd.DataFrame) -> None:
    """Bulk-insert the combined frame into the Hotel_Info table; raise on failure."""
    conn_string = f"""
    Driver={{{configscape.driver}}};
    Server={configscape.server_name};
    Database={configscape.database_name};
    Trusted_Connection=yes;
    """
    con = py.connect(conn_string)
    cursor = con.cursor()
    try:
        cursor.fast_executemany = True
        cursor.setinputsizes(configscape.inputsize)
        logger.info("Inserting %d rows into the database...", len(frame))
        cursor.executemany(configscape.query, frame_to_rows(frame))
        cursor.commit()
    finally:
        cursor.close()
        con.close()
        logger.info("Closed SQL connection.")
