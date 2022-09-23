from typing import List, Union

from fastapi import FastAPI

from view_models import DisposalSiteModel, DisposalItemModel, EventModel, QueryResultModel

app = FastAPI()


@app.get("/decision_tree")
async def get_decision_tree():
    return {"message": "Hello World"}


@app.get("/disposal_sites", response_model=List[DisposalSiteModel])
async def get_disposal_sites(long: Union[float, None] = None, lat: Union[float, None] = None,
                             radius: Union[int, None] = None, tags: Union[List[str], None] = None):
    return {}


@app.get("/disposal_items/{item_id}", response_model=DisposalItemModel)
async def get_disposal_item(item_id: str):
    return {}


@app.get("/events", response_model=List[EventModel])
async def get_events(
        long: Union[float, None] = None,
        lat: Union[float, None] = None,
        radius: Union[int, None] = None,
        timestamp_from: Union[int, None] = None,
        timestamp_to: Union[int, None] = None):
    return {}


@app.get("/search/query", response_model=List[QueryResultModel])
async def query_search(query: str):
    return {}


@app.post("/search/image", response_model=List[QueryResultModel])
async def image_search():
    return {}
