from typing import Mapping, Any, Union, List

from pymongo.database import Database

from view_models import DisposalSiteModel, \
    LocationModel


class DisposalSiteService:
    def __init__(self, db: Database[Mapping[str, Any]], language: str):
        self.db = db
        self.language = language

    def find_disposal_sites(self, long: Union[float, None] = None, lat: Union[float, None] = None,
                            radius: Union[int, None] = None,
                            bins: Union[List[str], None] = None) -> List[DisposalSiteModel]:
        aggregation = []

        if long is not None and lat is not None:
            innerFilter = {
                "near": {"type": "Point", "coordinates": [long, lat]},
                "includeLocs": "location",
                "distanceField": "distance",
            }
            if radius is not None:
                innerFilter["maxDistance"] = radius

            aggregation.append({"$geoNear": innerFilter})

        if bins is not None and len(bins) > 0:
            aggregation.append(
                {"$match": {"bins": {"$in": bins}}}
            )

        models = []
        for item in self.db["disposal_sites"].aggregate(aggregation):
            model = DisposalSiteModel(
                location=LocationModel(
                    lang=item["location"]["coordinates"][0],
                    lat=item["location"]["coordinates"][1]
                ),
                address=item["address"],
                bins=item["bins"]
            )

            if "distance" in item:
                model.distance = item["distance"]

            models.append(model)

        return models
