from typing import List, Union, Dict, Mapping, Any

from fastapi import FastAPI, Query
from pymongo import MongoClient
from pymongo.database import Database
from starlette.requests import Request

from service.restriction_service import RestrictionService
from view_models import DisposalSiteModel, DisposalItemModel, EventModel, QueryResultModel

app = FastAPI()
app.db: Database[Mapping[str, Any]]



connection_string = "mongodb://root:example@localhost"

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(connection_string)
    app.db = app.mongodb_client["appfall"]

    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.db.close()


@app.get("/restriction")
async def get_restriction(request: Request):
    attributes: Dict[str, str] = dict(request.query_params)

    return RestrictionService(app.db).get_restriction(attributes)


@app.get("/disposal_sites", response_model=List[DisposalSiteModel])
async def get_disposal_sites(long: Union[float, None] = None, lat: Union[float, None] = None,
                             radius: Union[int, None] = None,
                             tags: Union[List[str], None] = Query(None)):
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
