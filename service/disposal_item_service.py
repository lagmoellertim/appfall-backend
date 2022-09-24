from typing import Mapping, Any

from bson import ObjectId
from pymongo.database import Database

from view_models import DisposalItemModel, DisposalItemComponentModel


class DisposalItemService:
    def __init__(self, db: Database[Mapping[str, Any]], language: str):
        self.db = db
        self.language = language

    def get_item(self, item_id) -> DisposalItemModel:
        item = self.db["disposal_items"].find_one({"_id": ObjectId(item_id)})

        if item is None:
            raise ValueError("Item was not found")

        component_models = []
        for component in item["components"]:
            component_models.append(DisposalItemComponentModel(
                name=component["name"][self.language],
                bins=component["bins"]
            ))

        model = DisposalItemModel(
            id=item_id,
            name=item["name"][self.language],
            attributes=item["attributes"],
            components=component_models
        )

        if "info_text" in item:
            model.info_text = item["info_text"][self.language]

        return model