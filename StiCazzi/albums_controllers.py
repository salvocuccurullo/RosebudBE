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
from datetime import datetime

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
        special = i_data.get('special', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    logger.debug("="*80)
    logger.debug(i_data.get('query', ''))

    if not special and len(query) < 3:
        response['result'] = 'failure'
        response['message'] = 'Min query size is 3'
        response['status_code'] = 400
        return response

    now = datetime.now() # current date and time

    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    logger.debug("%s-%s-%s" % (year, month, day))
    logger.debug("special: %s" % special)
    logger.debug("="*80)

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    coll = db.cover

    if query and not special:
        mongo_stmt = { "$and": [
                        {"release_date": { "$exists": True }, "$expr": { "$gt": [{ "$strLenCP": '$release_date' }, 7] } },   #release date exists and its lenght > 7 (full date)
                        { "$or": [
                            {"name": { "$regex": query, "$options" : "i"}},
                            {"author": { "$regex": query, "$options" : "i"}},
                        ]}
                    ]}
    elif special and special == 'monthly':
        mongo_stmt = { "$and": [
                        {"release_date": { "$exists": True }, "$expr": { "$gt": [{ "$strLenCP": '$release_date' }, 7] } },#release date exists and its lenght > 7 (full date)
                        {"release_date": { "$regex": ".*\-%s\-.*" % month}}
                    ]}
    elif special and special == 'today':
        mongo_stmt = { "$and": [
                        {"release_date": { "$exists": True }, "$expr": { "$gt": [{ "$strLenCP": '$release_date' }, 7] } },#release date exists and its lenght > 7 (full date)
                        {"release_date": { "$regex": ".*\-%s\-%s" % (month, day)}}
                    ]}
    else:
        response['result'] = 'failure'
        response['message'] = 'Invalid data!'
        response['status_code'] = 400
        return response

    albums = coll.find(mongo_stmt)
    xyz = list(albums)
    xyz = [ \
        {
        "id": str(x['_id']),
        "title": x['name'], 
        "author": x['author'], 
        "location": x['location'],
        "spotifyAlbumUrl": x['spotifyAlbumUrl'],
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
    if remarkable == "yes":
        logger.debug("Setting remarkable flag (%s) for doc %s" % (remarkable, doc_id))
        remarkable = True
    else:
        logger.debug("Removing remarkable flag (%s) for doc %s" % (remarkable, doc_id))
        remarkable = False
    logger.debug("="*80)

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
