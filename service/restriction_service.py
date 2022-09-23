from collections import defaultdict
from typing import Mapping, Any, Dict, Set

from pymongo.database import Database

from view_models import RestrictionModel


class RestrictionService:
    def __init__(self, db: Database[Mapping[str, Any]]):
        self.db = db

    def get_restriction(self, attributes: Dict[str, str]) -> RestrictionModel:
        attribute_query = {f"attributes.{k}": v for k, v in attributes.items()}

        query = {**attribute_query}

        item_subset = list(self.db["disposal_items"].find(query))

        attribute_count_mapping: Dict[str, int] = defaultdict(int)
        for item in item_subset:
            for key, value in item["attributes"].items():
                attribute_count_mapping[key] += 1

        overarching_attributes: Set[str] = set(
            k for k, v in attribute_count_mapping.items() if v == len(item_subset)
        )
        other_attributes: Set[str] = (set(attribute_count_mapping.keys())
                                      .difference(overarching_attributes))

        return {"overarching_attributes": overarching_attributes,
                "other_attributes": other_attributes}
