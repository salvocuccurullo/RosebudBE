"""
    iCarusi BE - Albums Controller
"""

import os
import urllib
import json
import logging
import urllib.parse
import pprint
import pymongo
from pymongo import MongoClient, version
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date

from django.http import JsonResponse
from StiCazzi.controllers import authentication

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger(__name__)


@authentication
def get_stats(request):
    """ Get one album from Mongo """
    logger.debug("get statistics pymnongo called")
    response = {}

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    covers_c = db.command("collstats", "cover")
    songs_c = db.command("collstats", "song")
    response['payload'] = {}
    response['payload']['remote_covers'] = covers_c['count']     # backward compatibility, it will be fixed later
    response['payload']['remote_songs'] = songs_c['count']     # backward compatibility, it will be fixed later

    return response

@authentication
def get_one_album(request):
    """ Get one album from Mongo """
    logger.debug("get one album pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])

    db = client.rosebud_dev
    coll = db.cover

    try:
        res = coll.find_one({"_id": ObjectId(doc_id)})
        if res:
            response['album'] = \
            {
                "id": str(res['_id']),
                "title": res['name'],
                "author": res['author'],
                "location": res['location'],
                "thumbnail": res['thumbnail'],
                "spotifyAlbumUrl": res['spotifyAlbumUrl'],
                "release_date": res.get('release_date', ''),
                "remarkable": res.get('remarkable', '')
            }
    except Exception as e:
        response['result'] = 'failure'
        response['message'] = str(e)
        response['status_code'] = 400

    return response

@authentication
def set_one_album(request):
    """ Set one album on Mongo """
    logger.debug("set one album pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
        release_date = i_data.get('release_date', '')
        author = i_data.get('author', '')
        title = i_data.get('title', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])

    db = client.rosebud_dev
    coll = db.cover

    try:
        res = coll.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {
                    "release_date": release_date,
                    "author": author,
                    "name": title
                    }
                }
        )
    except Exception as e:
        response['result'] = 'failure'
        response['message'] = str(e)
        logger.error(str(e))
        response['status_code'] = 400

    return response

@authentication
def get_one_track(request):
    """ Get one track from Mongo """
    logger.debug("get one track pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])

    db = client.rosebud_dev
    coll = db.song

    try:
        res = coll.find_one({"_id": ObjectId(doc_id)})
        if res:
            response['song'] = \
            {
                "id": str(res['_id']),
                "title": res['name'],
                "author": res['author'],
                "location": res['location'],
                "thumbnail": res['thumbnail'],
                "spotifyAlbumUrl": res['spotifyAlbumUrl'],
                "release_date": res.get('release_date', ''),
                "remarkable": res.get('remarkable', '')
            }
    except Exception as e:
        response['result'] = 'failure'
        response['message'] = str(e)
        response['status_code'] = 400

    return response

@authentication
def set_one_track(request):
    """ Set one track on Mongo """
    logger.debug("set one track pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
        release_date = i_data.get('release_date', '')
        author = i_data.get('author', '')
        title = i_data.get('title', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])

    db = client.rosebud_dev
    coll = db.song

    try:
        res = coll.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {
                    "release_date": release_date,
                    "author": author,
                    "name": title
                    }
                }
        )
    except Exception as e:
        response['result'] = 'failure'
        response['message'] = str(e)
        logger.error(str(e))
        response['status_code'] = 400

    return response

@authentication
def delete_one_album(request):
    """ Delete one album from Mongo """
    logger.debug("delete one album pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])

    db = client.rosebud_dev
    coll = db.cover

    try:
        res = coll.delete_one(
            {"_id": ObjectId(doc_id)}
        )
    except Exception as e:
        response['result'] = 'failure'
        response['message'] = str(e)
        logger.error(str(e))
        response['status_code'] = 400

    return response

@authentication
def delete_track(request):
    """ Delete one track from Mongo """
    logger.debug("delete one track pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        doc_id = i_data.get('doc_id', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])

    db = client.rosebud_dev
    coll = db.song

    try:
        res = coll.delete_one(
            {"_id": ObjectId(doc_id)}
        )
    except Exception as e:
        response['result'] = 'failure'
        response['message'] = str(e)
        logger.error(str(e))
        response['status_code'] = 400

    return response

@authentication
def get_spotify_albums_x_artist(request):
    """ Get all the albums for an artist from SPOTIFY API """
    logger.debug("get albums for artist pymnongo called")
    response = {}

    try:
        i_data = json.loads(request.body)
        spotify_id = i_data.get('spotify_id', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    spoty_uri = 'spotify:artist:%s' % spotify_id
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.artist_albums(spoty_uri, album_type='album')

    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])

    albums = [
        { "title": x['name'],
          "picture": (x['images'] or [{'url': './images/no-image-available.jpg'}])[0]['url'],
          "id":  x['id'],
          "uri":  x['uri'],
          "url": x['external_urls']['spotify'],
          "release_date": x['release_date']
        } for x in albums  ]
    albums = sorted(albums, key=lambda d: d['release_date'])

    return albums

@authentication
def get_spotify_artists(request):
    """ Get artists from SPOTIFY API """
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

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.search(query, type='artist')

    artists = [
        { "title": x['name'],
          "picture": x['images'][0]['url'],
          "id":  x['id'],
          "uri":  x['uri'],
          "url": x['external_urls']['spotify']
        } for x in results['artists']['items'] if len(x['images']) > 0 ]

    return artists

@authentication
def get_spotify_tracks(request):
    """ Get artists from SPOTIFY API """
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

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.search(query, type='track')
    #logger.debug(pprint.pprint(results))

    tracks = [
        { "title": x['name'],
          "picture": x['album']['images'][0]['url'],
          "release_date": x['album']['release_date'],
          "author": x['artists'][0]['name'],
          "id":  x['id'],
          "uri":  x['uri'],
          "url": x['external_urls']['spotify']
        } for x in results['tracks']['items'] if len(x['album']['images']) > 0 ]

    return tracks

@authentication
def add_album(request):
    """
        Add new album on MongoDB. Data is retrieved from Spotify
        There is a precheck in place for avoiding to add an existent album
    """
    logger.debug("add album to MongoDB")
    response = {}

    try:
        i_data = json.loads(request.body)
        spotify_id = i_data.get('spotify_id', '')
        username = i_data.get('username', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    try:
        client = MongoClient()
        client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
        db = client.rosebud_dev
        coll = db.cover

        spotify_url = "https://open.spotify.com/album/%s" % spotify_id
        mongo_stmt = {"spotifyAlbumUrl": spotify_url}
        res = coll.find(mongo_stmt)
        xyz = list(res)

        if len(xyz):
            response['found'] = True
            response['spotifyAlbumUrl'] = spotify_url
            response['mongodb_doc_id'] = str(xyz[0]['_id'])
            response['message'] = 'This album already exists on Mongodb'
            return response
        else:
            response['found'] = False

        now = datetime.now()
        now = now.replace(microsecond=0)
        pretty_now = now.strftime("%Y/%m/%d %H:%M:%S")


        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        album = spotify.album(spotify_id)

        mongo_doc = {}
        mongo_doc['name'] = album['name']
        mongo_doc['author'] = album['artists'][0]['name']
        mongo_doc['release_date'] = album['release_date']
        mongo_doc['year'] = album['release_date'][0:4]
        mongo_doc['location'] = album['release_date'][0:4]
        mongo_doc['spotifyAlbumUrl'] = album['external_urls']['spotify']
        mongo_doc['spotifyUrl'] = album['href']
        mongo_doc['remarkable'] = False
        mongo_doc['username'] = username
        mongo_doc['location'] = (album['images'] or [{'url': './images/no-image-available.jpg'}])[0]['url']
        mongo_doc['filename'] = (album['images'] or [{'url': './images/no-image-available.jpg'}])[0]['url']
        mongo_doc['thumbnail'] = (album['images'] or [{'url': './images/no-image-available.jpg'}])[2]['url']
        mongo_doc['create_ts'] = now
        mongo_doc['update_ts'] = now
        mongo_doc['created'] = pretty_now
        mongo_doc['type'] = 'remote'

        coll.insert_one(mongo_doc)

        mongo_doc['_id'] = str(mongo_doc['_id'])
        response['album'] = mongo_doc
        response['message'] = 'Album \'%(name)s\' by \'%(author)s\' saved on Mongodb - Id: %(_id)s' % mongo_doc

    except Exception as ee:
        response['message'] = str(ee)
        response['failure'] = True

    return response

@authentication
def add_track(request):
    """
        Add new track on MongoDB. Data is retrieved from Spotify
        There is a precheck in place for avoiding to add an existent track
    """
    logger.debug("add track to MongoDB")
    response = {}

    try:
        i_data = json.loads(request.body)
        spotify_id = i_data.get('spotify_id', '')
        username = i_data.get('username', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    try:
        client = MongoClient()
        client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
        db = client.rosebud_dev
        coll = db.song

        spotify_url = "https://open.spotify.com/album/%s" % spotify_id
        mongo_stmt = {"spotifyAlbumUrl": spotify_url}
        res = coll.find(mongo_stmt)
        xyz = list(res)

        if len(xyz):
            response['found'] = True
            response['spotifyAlbumUrl'] = spotify_url
            response['mongodb_doc_id'] = str(xyz[0]['_id'])
            response['message'] = 'This album already exists on Mongodb'
            return response
        else:
            response['found'] = False

        now = datetime.now()
        now = now.replace(microsecond=0)
        pretty_now = now.strftime("%Y/%m/%d %H:%M:%S")

        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        track = spotify.track(spotify_id)
        #logger.debug(pprint.pprint(track))

        mongo_doc = {}
        mongo_doc['name'] = track['name']
        mongo_doc['author'] = track['artists'][0]['name']
        mongo_doc['release_date'] = track['album']['release_date']
        mongo_doc['year'] = track['album']['release_date'][0:4]
        mongo_doc['spotifyAlbumUrl'] = track['external_urls']['spotify']
        mongo_doc['spotifyUrl'] = track['href']
        mongo_doc['remarkable'] = False
        mongo_doc['username'] = username
        mongo_doc['location'] = (track['album']['images'] or [{'url': './images/no-image-available.jpg'}])[0]['url']
        mongo_doc['filename'] = (track['album']['images'] or [{'url': './images/no-image-available.jpg'}])[0]['url']
        mongo_doc['thumbnail'] = (track['album']['images'] or [{'url': './images/no-image-available.jpg'}])[2]['url']
        mongo_doc['create_ts'] = now
        mongo_doc['update_ts'] = now
        mongo_doc['created'] = pretty_now
        mongo_doc['type'] = 'remote'

        coll.insert_one(mongo_doc)

        mongo_doc['_id'] = str(mongo_doc['_id'])
        response['track'] = mongo_doc
        response['message'] = 'Track \'%(name)s\' by \'%(author)s\' saved on Mongodb - Id: %(_id)s' % mongo_doc

    except Exception as ee:
        response['message'] = str(ee)
        response['failure'] = True

    return response

@authentication
def get_albums(request):
    """ Get albums from MongoDB """
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

    #logger.debug("="*80)
    #logger.debug(i_data.get('query', ''))

    if not special and len(query) < 3:
        response['result'] = 'failure'
        response['message'] = 'Min query size is 3'
        response['status_code'] = 400
        logger.debug("no special and query length < 3")
        return response

    today = date.today() # current date
    if special and special == "yesterday":
        today = today + timedelta(days=-1)
    elif special and special == "tomorrow":
        today = today + timedelta(days=+1)

    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    #logger.debug("special: %s" % special)
    #logger.debug("%s-%s-%s" % (year, month, day))
    #logger.debug("="*80)

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    coll = db.cover

    if query and special and special in ('all'):
        mongo_stmt = { "$or": [
                        {"name": { "$regex": query, "$options" : "i"}},
                        {"author": { "$regex": query, "$options" : "i"}},
                    ]}
    elif query and not special:
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
    elif special and special in ('today', 'yesterday', 'tomorrow'):
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
        "thumbnail": x['thumbnail'],
        "spotifyAlbumUrl": x['spotifyAlbumUrl'],
        "release_date": x.get('release_date', ''), 
        "remarkable": x.get('remarkable', '')
        } for x in xyz]

    response["query"] = query
    response["albums"] = xyz
    response["size"] = len(xyz)

    return response

@authentication
def get_tracks(request):
    """ Get tracks from MongoDB """
    logger.debug("get tracks pymnongo called")
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

    #logger.debug("="*80)
    #logger.debug(i_data.get('query', ''))

    if not special and len(query) < 3:
        response['result'] = 'failure'
        response['message'] = 'Min query size is 3'
        response['status_code'] = 400
        logger.debug("no special and query length < 3")
        return response

    today = date.today() # current date
    if special and special == "yesterday":
        today = today + timedelta(days=-1)
    elif special and special == "tomorrow":
        today = today + timedelta(days=+1)

    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    #logger.debug("special: %s" % special)
    #logger.debug("%s-%s-%s" % (year, month, day))
    #logger.debug("="*80)

    client = MongoClient()
    client = MongoClient(os.environ['MONGO_SERVER_URL_PYMONGO'])
    db = client.rosebud_dev
    coll = db.song

    if query and special and special in ('all'):
        mongo_stmt = { "$or": [
                        {"name": { "$regex": query, "$options" : "i"}},
                        {"author": { "$regex": query, "$options" : "i"}},
                    ]}
    elif query and not special:
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
    elif special and special in ('today', 'yesterday', 'tomorrow'):
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
        "thumbnail": x['thumbnail'],
        "spotifyAlbumUrl": x['spotifyAlbumUrl'],
        "release_date": x.get('release_date', ''), 
        "remarkable": x.get('remarkable', '')
        } for x in xyz]

    response["query"] = query
    response["tracks"] = xyz
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
        item_type = i_data.get('item_type', '')
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
    if item_type == "album":
        coll = db.cover
    elif item_type == "track":
        coll = db.song
    res = coll.update_one( 
            { "_id": ObjectId(doc_id) },
            { "$set": { "remarkable": remarkable } }
          )
    #logger.debug(pprint.pprint(res))

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
