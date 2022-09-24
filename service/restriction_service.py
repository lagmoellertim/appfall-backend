import base64
import pickle

import numpy
import numpy as np
from collections import defaultdict
from typing import Mapping, Any, Dict, Set, Optional, Tuple, List

from pymongo.database import Database

from view_models import RestrictionModel, QuestionModel, AnswerModel, \
    RestrictionDisposableItemModel, AdditionalAttributeModel


class RestrictionService:
    def __init__(self, db: Database[Mapping[str, Any]], language: str, model, clip_model,
                 tokenizer):
        self.db = db
        self.language = language
        self.model = model
        self.clip_model = clip_model
        self.tokenizer = tokenizer

    @staticmethod
    def __calculate_attribute_score(value_count_mapping: List[int]) -> float:
        if len(value_count_mapping) == 1:
            return 0.0
        _sum = 0
        for count in value_count_mapping:
            _sum += (count / sum(value_count_mapping)) * (sum(value_count_mapping) - count)
        return _sum / len(value_count_mapping)

    def get_restriction(self, attributes: Dict[str, str]) -> RestrictionModel:

        item_subset, next_best_attribute, is_using_other_attributes = self.get_item_subset_and_next_best_attribute(
            attributes)

        model = RestrictionModel(
            possible_disposal_items=self.get_restriction_disposable_item_model(item_subset)
        )

        if next_best_attribute is not None:
            question_model = self.get_question_model(next_best_attribute, is_using_other_attributes)
            model.question = question_model

        return model

    def get_restriction_disposable_item_model(
            self,
            item_subset
    ) -> List[RestrictionDisposableItemModel]:

        item_mapping: Dict[str, List[str]] = defaultdict(list)

        for item in item_subset:
            key = item["name"][self.language]
            item_mapping[key].append(str(item["_id"]))

        result: List[RestrictionDisposableItemModel] = []

        for key, ids in list(item_mapping.items()):
            model = RestrictionDisposableItemModel(name=key)

            if len(ids) == 1:
                model.id = ids[0]
            else:
                model.additional_attribute = AdditionalAttributeModel(key="name", value=key)

            result.append(model)

        return result

    def get_question_model(self, attribute, is_using_other_attributes: bool) -> QuestionModel:
        next_question = self.db["questions"].find_one({"attribute": attribute})

        if next_question is None:
            raise ValueError(f"No Question found for attribute {attribute}")

        answers = []
        for attribute_value, answer in next_question["answers"].items():
            answer_model = AnswerModel(
                answer_text=answer["text"][self.language],
                attribute_value=attribute_value,
                metadata=answer["metadata"]
            )
            answers.append(answer_model)

        # add default if question is of attributes which are not matching for all items
        if is_using_other_attributes:
            answer_text = "Does not match" if self.language == "en" else "Trifft nicht zu"
            answers.append(AnswerModel(
                answer_text=answer_text,
                attribute_value='null',
                metadata="does_not_match"
            ))

        return QuestionModel(
            question_text=next_question["question"][self.language],
            attribute_key=attribute,
            answers=answers
        )

    def get_ai_filtered_subset(self, ai_attribute_value, item_subset, hash_from_image) -> List[Any]:
        decoded_bytes = base64.decodebytes(ai_attribute_value.encode("utf-8"))
        np_embedding: np.ndarray = np.frombuffer(decoded_bytes, dtype=np.float32).reshape([512])
        np_embedding = np_embedding / np.linalg.norm(np_embedding, axis=-1, keepdims=True)

        filtered_item_set = []
        for (i, item) in enumerate(item_subset):
            if "ai_hash" not in item:
                continue
            embedding = pickle.loads(item["ai_hash"])
            embedding = embedding / np.linalg.norm(embedding, axis=-1, keepdims=True)
            similarity = np_embedding @ embedding.T

            filtered_item_set.append((i, similarity))
        filtered_item_set.sort(key=lambda x: x[1], reverse=True)

        min_score = 0.8
        if hash_from_image:
            min_score = 0.3

        return [item_subset[i] for i, sim in filtered_item_set if sim > min_score]

    def get_item_subset_and_next_best_attribute(
            self,
            attributes: Dict[str, str]
    ) -> Tuple[Any, Optional[str], bool]:

        attribute_query = {}

        # get filters on attributes
        for k, v in attributes.items():
            # check if selection is fall-back for attributes which are not valid for all item
            if v == "null":
                continue

            # check special filter for item-name
            if k == "name":
                attribute_query[f"name.{self.language}"] = v
                continue

            if k == "ai-text":
                continue

            if k == "ai-image":
                continue

            attribute_query[f"attributes.{k}"] = v

        item_subset = list(self.db["disposal_items"].find(attribute_query))

        if "ai-text" in attributes:
            item_subset = self.get_ai_filtered_subset(attributes["ai-text"], item_subset, False)
        elif "ai-image" in attributes:
            item_subset = self.get_ai_filtered_subset(attributes["ai-image"], item_subset, True)

        # if there is just one result we are done
        if len(item_subset) == 1:
            return item_subset, None, False

        # get appearance of value per attribute
        attribute_count_mapping: Dict[str, int] = defaultdict(int)
        for item in item_subset:
            for key, value in item["attributes"].items():
                if key in attributes:
                    continue
                attribute_count_mapping[key] += 1

        # check if no answers are left
        if len(attribute_count_mapping) == 0:
            return item_subset, None, False

        # get attributes which appear in every item
        overarching_attributes: Set[str] = set(
            k for k, v in attribute_count_mapping.items() if v == len(item_subset)
        )
        # or not
        other_attributes: Set[str] = (set(attribute_count_mapping.keys())
                                      .difference(overarching_attributes))
        potential_attributes = overarching_attributes
        is_using_other_attributes = len(potential_attributes) == 0
        if is_using_other_attributes:
            potential_attributes = other_attributes

        attribute_value_count_mapping: Dict[str, Dict[str, int]] = {attr: defaultdict(int) for attr
                                                                    in potential_attributes}

        for attr in potential_attributes:
            for item in item_subset:
                try:
                    attribute_value_count_mapping[attr][item["attributes"][attr]] += 1
                except Exception:
                    pass

        attribute_scores: Dict[str, float] = {}
        for attr, value_count in attribute_value_count_mapping.items():
            try:
                value_counts = list(value_count.values())
                attribute_scores[attr] = self.__calculate_attribute_score(value_counts)
            except ZeroDivisionError:
                pass

        if len(attribute_scores) == 0:
            return item_subset, None, False

        best_attribute_choice = \
            sorted(attribute_scores.items(), key=lambda x: x[1], reverse=True)[0][0]

        return item_subset, best_attribute_choice, is_using_other_attributes
