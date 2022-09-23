from typing import Union, List

from pydantic import BaseModel


class LocationModel(BaseModel):
    lang: float
    lat: float


class DisposalSiteModel(BaseModel):
    id: str
    name: str
    info: str
    location: LocationModel
    tags: List[str]


class DisposalItemModel(BaseModel):
    id: str
    name: str
    tags: List[str]


class EventModel(BaseModel):
    id: str
    name: str
    timestamp: int
    location: Union[LocationModel, str]


class QueryResultModel(BaseModel):
    id: str
    name: str
    confidence: float
