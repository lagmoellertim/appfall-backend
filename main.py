import io
import os
from typing import List, Union, Dict, Mapping, Any

import pymongo

import clip
import transformers
from PIL import Image
from fastapi import FastAPI, Query, UploadFile
from multilingual_clip import pt_multilingual_clip
from pymongo import MongoClient
from pymongo.database import Database
from starlette.requests import Request

from service.disposal_item_service import DisposalItemService
from service.disposal_site_service import DisposalSiteService
from service.restriction_service import RestrictionService
from view_models import DisposalSiteModel, DisposalItemModel, EventModel, QueryResultModel, \
    AdditionalAttributeModel
from fastapi.middleware.cors import CORSMiddleware

import base64

app = FastAPI()
app.db: Database[Mapping[str, Any]]

model_name = 'M-CLIP/XLM-Roberta-Large-Vit-B-32'
clip_model_name = "ViT-B/32"


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_language_from_header(request: Request):
    try:
        language = request.headers["Accept-Language"]
        return language.split("-")[0].split(",")[0].split(";")[0]
    except Exception:
        return "en"


mongo_user = os.environ.get("DB_USER") or "root"
mongo_pass = os.environ.get("DB_PASS") or "example"
mongo_host = os.environ.get("DB_HOST") or "localhost"
connection_string = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}"


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(connection_string)
    app.db = app.mongodb_client["appfall"]
    app.db["disposal_sites"].create_index([("location", pymongo.GEOSPHERE)])
    if os.environ.get("LOAD_AI") == "true":
        app.model = pt_multilingual_clip.MultilingualCLIP.from_pretrained(model_name, cache_dir="clip")
        app.clip_model, app.clip_preprocess = clip.load(clip_model_name, device="cpu", download_root="clip")
        app.tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.db.close()


@app.get("/restriction")
async def get_restriction(request: Request):
    language = extract_language_from_header(request)
    attributes: Dict[str, str] = dict(request.query_params)

    return RestrictionService(app.db, language, app.model, app.clip_model, app.tokenizer).get_restriction(attributes)


@app.get("/disposal_sites", response_model=List[DisposalSiteModel])
async def get_disposal_sites(request: Request, long: Union[float, None] = None, lat: Union[float, None] = None,
                             radius: Union[int, None] = None,
                             bin: Union[str, None] = None):
    language = extract_language_from_header(request)

    return DisposalSiteService(app.db, language).find_disposal_sites(long, lat, radius, bin)


@app.get("/disposal_items/{item_id}", response_model=DisposalItemModel)
async def get_disposal_item(request: Request, item_id: str):
    language = extract_language_from_header(request)

    if item_id is None or item_id == "":
        raise ValueError("No item id was supplied")

    return DisposalItemService(app.db, language).get_item(item_id)


@app.get("/events", response_model=List[EventModel])
async def get_events(
        long: Union[float, None] = None,
        lat: Union[float, None] = None,
        radius: Union[int, None] = None,
        timestamp_from: Union[int, None] = None,
        timestamp_to: Union[int, None] = None):
    return {}


@app.get("/search/query", response_model=AdditionalAttributeModel)
async def query_search(q: str = None):
    if not q:
        raise ValueError("Invalid query parameter")

    embeddings = app.model.forward([q], app.tokenizer)
    np_embedding = embeddings[0].detach().numpy()

    encoded_embedding = base64.b64encode(np_embedding)

    return AdditionalAttributeModel(
        key="ai-text",
        value=encoded_embedding
    )


@app.post("/search/image", response_model=AdditionalAttributeModel)
async def image_search(file: UploadFile):
    request_object_content = await file.read()
    image = app.clip_preprocess(Image.open(io.BytesIO(request_object_content))).unsqueeze(0).to("cpu")
    image_features = app.clip_model.encode_image(image)[0].detach().numpy()

    print(image_features)

    encoded_embedding = base64.b64encode(image_features)

    return AdditionalAttributeModel(
        key="ai-image",
        value=encoded_embedding
    )
