"""API main file."""

from fastapi import FastAPI, Query

from .database.database_utils import get_search_result
from .database.models import Car

app = FastAPI()


# @app.get("/")
# def read_root()->dict[str,str]:
#     return {"Hello": "World"}


@app.get("/search")
def search(search_query: str, n_results: int = Query(default=10, le=50)) -> list[Car]:
    """Return Cars matching the query.

    The distance for each result in included in the response.

    Args:
        search_query: Informations about a car..
        n_results: Number of results provided by the route
    """
    return get_search_result(search_query=search_query, n_results=n_results)
