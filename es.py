from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os
import json


def read_data(path):
    with open(path, 'r', encoding='UTF-8') as file:
        data = json.loads(file.read())
    return data


def load_data(index_name):
    many_items = True
    all_data = read_data(os.path.join(os.curdir, "src", "articles-info.json"))
    if many_items:
        for i, item in enumerate(all_data, 1):
            print(f'Processing {i} of {len(all_data)} ...')
            yield {
                "_index": index_name,
                "_source": item
            }
        else:
            yield {
                "_index": index_name,
                "_source": all_data
            }


def index_processing(es_object, index_name, mappings):
    created = False
    try:
        if not es.indices.exists(index_name):
            settings = {
                'settings': {
                    'number_of_shards': 1,
                    'number_of_replicas': 0
                },
                **mappings
            }
            es_object.indices.create(index=index_name, ignore=400, body=settings)
        else:
            print("Index is already exists")
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


if __name__ == '__main__':
    es = Elasticsearch("http://194.85.206.38/elasticsearch/", port=80, http_auth="dyakovlev:dLrYa6")
    index_name = 'SpringerOpen'
    # es.index(index_name)
    mappings = read_data(os.path.join(os.curdir, "src", "mappings.json"))
    if index_processing(es, index_name, mappings):
        bulk(es, load_data(index_name))
