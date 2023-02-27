"""
    iCarusi BE - Albums Controller
"""

import os
import urllib
import json
import logging
import urllib.parse
import pprint
from pymongo import MongoClient
from bson.objectid import ObjectId

from django.http import JsonResponse
from StiCazzi.controllers import authentication

logger = logging.getLogger(__name__)

@authentication
def get_albums(request):
    """ Get a random cover from API """
    logger.debug("get albums pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        query = i_data.get('query', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    logger.debug("="*80)
    logger.debug(i_data.get('query', ''))
    logger.debug("="*80)

    if len(query) < 3:
        response['result'] = 'failure'
        response['message'] = 'Min query size is 3'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    coll = db.cover
    albums = coll.find( \
          { "$and": [
            { "$or": [
              {"name": { "$regex": query}},
              {"author": { "$regex": query}},
            ]},
            {"release_date": { "$exists": True }, "$expr": { "$gt": [{ "$strLenCP": '$release_date' }, 7] } }   #release date exists and its lenght > 7 (full date)
          ]}
          )
    xyz = list(albums)
    xyz = [ \
        {
        "id": str(x['_id']),
        "title": x['name'], 
        "author": x['author'], 
        "release_date": x.get('release_date', ''), 
        "remarkable": x.get('remarkable', '')
        } for x in xyz]

    response["query"] = query
    response["albums"] = xyz
    response["size"] = len(xyz)

    return response


@authentication
def set_remarkable(request):
    """ Get a random cover from API """
    logger.debug("set remarkable pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
        remarkable = i_data.get('remarkable', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    logger.debug("="*80)
    logger.debug(doc_id)
    logger.debug(remarkable)
    logger.debug("="*80)
    
    if remarkable == "True" or remarkable == "true" or remarkable == "on" or remarkable == "1":
      remarkable = True
    else:
      remarkable = False

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    coll = db.cover
    res = coll.update_one( 
            { "_id": ObjectId(doc_id) },
            { "$set": { "remarkable": remarkable } }
          )
    logger.debug(pprint.pprint(res))

    return response

@authentication
def get_random_album(request):
    """ Get a random cover from API """
    logger.debug("get random album pymnongo called")
    response = {}

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    coll = db.cover
    album = list(coll.aggregate([{ "$sample": { "size": 1 } }]))[0]
    response = {
          "name": album['name'],
          "author": album['author'],
          "location": album['location'],
          "spotifyAlbumUrl": album['spotifyAlbumUrl'],
          "type": album['type'],
    }

    return response
