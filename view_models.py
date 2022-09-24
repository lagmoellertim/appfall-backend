from typing import Union, List, Optional, Tuple, Dict

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
    info_text: Optional[str]
    location: LocationModel
    address: str
    bins: List[str]


class DisposalItemComponentModel(BaseModel):
    name: str
    bin: str


class DisposalItemModel(BaseModel):
    id: str
    name: str
    components: List[DisposalItemComponentModel]
    info_text: Optional[str]
    attributes: Dict[str, str]


class EventModel(BaseModel):
    id: str
    name: str
    timestamp: int
    location: str


class QueryResultModel(BaseModel):
    detection_result_text: str
    attribute_value: str
    confidence: float
