"""Interface for the sqlite and annoy db."""

import os
import sqlite3

import pandas as pd
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer

from .models import Car

# MODEL_NAME: str = "all-MiniLM-L6-v2"
# VECTOR_SIZE: int = 384

MODEL_NAME: str = "all-mpnet-base-v2"
VECTOR_SIZE: int = 768

MODEL: SentenceTransformer = SentenceTransformer(MODEL_NAME)

N_TREES: int = 500
# SEARCH_K: int = 1000
DISTANCE_METHOD: str = "euclidean"

ANNOY_DATABASE_PATH: str = "./database/vec_db.ann"
CSV_PATH: str = "./database/cars.csv"
SQLITE_DATABASE_PATH: str = "./database/cars.db"
SCHEMA_PATH: str = "./database/schema.sql"


# Error definition
class DbError(Exception):
    """Error thrown when an error occur with one of the database."""

    pass


# Creation of the bds if not already created
def fill_annoy_database() -> AnnoyIndex:
    """Create and fill the Annoy database. It can take a lot of time."""
    # load csv file
    df: pd.DataFrame = pd.read_csv(CSV_PATH)

    vectors = MODEL.encode(
        sentences=df["full_description"].tolist(),
        show_progress_bar=True,
    )

    # store every vectorsin the database
    database_index: AnnoyIndex = AnnoyIndex(VECTOR_SIZE, DISTANCE_METHOD)

    for i, vector in enumerate(vectors):
        database_index.add_item(i, vector)
    database_index.build(N_TREES, n_jobs=-1)
    database_index.save(ANNOY_DATABASE_PATH)

    return database_index


def create_sqlite_database_from_csv() -> None:
    """Create the sqlite database.

    It only work if any sqlite database is found at the SQLITE_DATABASE_PATH. It also
    create table according to the schema.sql file provided at SCHEMA_PATH.
    Table created: Cars.
    """
    # Check if the database file exists
    if not os.path.exists(SQLITE_DATABASE_PATH):
        # Create the DB
        db_conn = sqlite3.connect(SQLITE_DATABASE_PATH)
        db_cursor: sqlite3.Cursor = db_conn.cursor()

        # Create tables
        with open(SCHEMA_PATH) as schema_file:
            schema_content: list[str] = schema_file.read().split(";")
            for sql_order in schema_content:
                db_cursor.execute(sql_order.strip())

        # Fill the DB
        df = pd.read_csv(CSV_PATH)
        df.to_sql("CARS", db_conn, if_exists="replace", index=False)
        db_conn.commit()
        db_conn.close()


create_sqlite_database_from_csv()

if os.path.exists(ANNOY_DATABASE_PATH):
    DATABASE_INDEX: AnnoyIndex = AnnoyIndex(VECTOR_SIZE, DISTANCE_METHOD)
    DATABASE_INDEX.load(ANNOY_DATABASE_PATH)
else:
    DATABASE_INDEX: AnnoyIndex = fill_annoy_database()  # type: ignore


def get_car_by_id(car_id: int, dist: float) -> Car:
    """Find and return a car from the sqlite database.

    It create the Car object with the distance from search associated.

    Args:
        car_id: The id of the car to find in the database.
        dist: The distance which will be set to the Car object of the response

    Return:
        The Car find in the sqlite database.

    Raises:
        DbError when there is no matching car in the database.
    """
    # request the database
    db_connection: sqlite3.Connection = sqlite3.connect(SQLITE_DATABASE_PATH)
    db_cursor: sqlite3.Cursor = db_connection.cursor()

    car: list[tuple[str, str]] = db_cursor.execute(
        """
        SELECT car_name, full_description from CARS where id=?;
        """,
        (car_id,),
    ).fetchall()
    db_connection.commit()
    db_connection.close()

    if len(car) != 1:
        raise DbError("There is no matching car in the database.")

    return Car(name=car[0][0], description=car[0][1], distance=dist)


def get_search_result(search_query: str, n_results: int) -> list[Car]:
    """Return Cars matching the query.

    Args:
        search_query: Informations about a car..
        n_results: Number of results provided by the route
    """
    search_input_embed: list[list[float]] = MODEL.encode(sentences=[search_query])
    matching_document_id: tuple[list[int], ...] = DATABASE_INDEX.get_nns_by_vector(
        vector=search_input_embed[0],
        n=n_results,
        # search_k=SEARCH_K,
        include_distances=True,
    )
    return [
        get_car_by_id(car_id=matching_document_id[0][i], dist=matching_document_id[1][i])
        for i in range(len(matching_document_id[0]))
    ]
