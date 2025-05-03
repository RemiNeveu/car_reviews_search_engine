"""Front for the car search engine."""

import requests
import streamlit as st
from pydantic import BaseModel

API_URL: str = "10.5.0.5:8000"


class Car(BaseModel):  # type: ignore
    """Model use to represent object send by the API."""

    name: str
    description: str
    distance: float


def get_search_results(search_query: str, n_results: int) -> list[Car]:
    """Request the API to get search results.

    Args:
        search_query: The query to send.
        n_results: the number of results needed.
    """
    api_url = f"http://{API_URL}/search"
    params = {"search_query": search_query, "n_results": n_results}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:  # noqa: PLR2004
        return [Car(**car) for car in response.json()]
    st.error(f"Error: {response.status_code} - {response.text}")
    return []


# Streamlit app layout
st.title("Car reviews search engine")

# Input fields
search_query = st.text_input("Enter your search query:")
n_results = st.number_input("Number of results:", min_value=1, max_value=100, value=5)

# Search button
if st.button("Search"):
    if search_query:
        results = get_search_results(search_query, n_results)
        if results:
            st.success(f"Found {len(results)} results:")
            for car in results:
                st.write(f"**Name:** {car.name}")
                st.write(f"**Distance:** {car.distance}")
                with st.expander("Description"):
                    st.write(car.description)
                st.write("---")
        else:
            st.warning("No results found.")
    else:
        st.warning("Please enter a search query.")
