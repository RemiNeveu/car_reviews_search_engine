# Car reviews search engine
The goal of the project is to provide a simple search engine built entirely in Python. The documents used as the database are from the [expert-car-reviews-dataset](https://www.kaggle.com/datasets/ademboukhris/expert-car-reviews-dataset).


# Launch the stack
```bash
docker compose up
```
- The API is available on [http://localhost:8000](http://localhost:8000). (You can access the swagerUI : [http://localhost:8000/docs](http://localhost:8000/docs))
- The front is available on [http://localhost:8001](http://localhost:8001).


# Project details
There are two parts to the project, each running in its own container and communicating through HTTP.

## Back
The API is built with the [FastAPI](https://fastapi.tiangolo.com/) framework and has a single route, `search`, which allows sending a query and the desired number of results. The API is connected to two databases:

The first is a SQLite database containing the textual version of each document.
The second is a vector database using the [Annoy](https://github.com/spotify/annoy) library. This database contains the same data in vector form.
The model used to generate the embeddings of the documents and user queries is all-mpnet-base-v2, used with the [sentence-transformers](https://github.com/UKPLab/sentence-transformers) library. This model provides 768-dimensional vectors, offering a good compromise that allows processing texts longer than a single sentence while requiring reasonable time and resources.
A match is then made between the two databases to return the original document in its textual form.

## Front
The front is build with [streamlit](https://streamlit.io/).
