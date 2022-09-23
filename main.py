from typing import List, Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/decision_tree")
async def get_decision_tree():
    return {"message": "Hello World"}


@app.get("/disposal_sites")
async def get_disposal_sites(long: Union[float, None] = None, lat: Union[float, None] = None,
                             radius: Union[int, None] = None, tags: Union[List[str], None] = None):
    return {}


@app.get("/disposal_items/{item_id}")
async def get_disposal_item(item_id: str):
    return {}


@app.get("/events")
async def get_events(
        long: Union[float, None] = None,
        lat: Union[float, None] = None,
        radius: Union[int, None] = None,
        timestamp_from: Union[int, None] = None,
        timestamp_to: Union[int, None] = None):
    return {}


@app.get("/search/query")
async def query_search(query: str):
    return {}


@app.post("/search/image")
async def image_search():
    return {}
