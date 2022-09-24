import csv
from pymongo import MongoClient
import pymongo

client = MongoClient("mongodb://root:example@localhost:27017/")
mydb = client["Appfall"]
mycol = mydb["disposal_items"]

mycol.drop()


with open('items.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0

    attr_names = [
        'category',
        'material',
        'is_functionable',
        'is_clean',
        'is_wearable',
        'is_electric',
        'contained_food'
    ]

    for row in csv_reader:
        names = {}
        attributes = {}
        components = []

        names['de'] = row[0]
        names['en'] = row[1]

        if line_count < 2:
            line_count += 1
            continue

        for index, attr in enumerate(row[2: 6]):
            if attr == "":
                continue
            attributes[attr_names[index]] = attr

        components.append({
            'name': {
                'de': 'Alles',
                'en': 'all'
            },
            'bin': row[12]
        })

        mycol.insert_one({
            "name": names,
            "attributes": attributes,
            'components': components,
            'info_text': row[10],
        })
