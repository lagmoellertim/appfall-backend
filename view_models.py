from typing import Union, List, Optional, Tuple

from pydantic import BaseModel


class LocationModel(BaseModel):
    lang: float
    lat: float


class AnswerModel(BaseModel):
    answer_text: str
    attribute_value: str
    metadata: str


class QuestionModel(BaseModel):
    question_text: str
    attribute_key: str
    answers: List[AnswerModel]


class AdditionalAttributeModel(BaseModel):
    key: str
    value: str


class RestrictionDisposableItemModel(BaseModel):
    name: str
    id: Optional[str]
    additional_attribute: Optional[AdditionalAttributeModel]


class RestrictionModel(BaseModel):
    question: Union[QuestionModel, None]
    possible_disposal_items: List[RestrictionDisposableItemModel]


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
    detection_result_text: str
    attribute_value: str
    confidence: float
