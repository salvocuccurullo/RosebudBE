"""
 Controller: login and generic
"""

import json
import base64
import os
import logging
import uuid

from random import randint
from datetime import datetime
import datetime as dttt
from Crypto.Cipher import AES
import Padding
import requests
from requests.auth import HTTPBasicAuth

import firebase_admin
from firebase_admin import credentials, auth
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import git

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from django.core import serializers
from django import get_version
from django.contrib.auth import authenticate
from django.utils import timezone


from StiCazzi.models import Pesata, Soggetto, Song, Lyric, Movie, User, Session, Location, Configuration, Notification, UserDevice
from StiCazzi.models import ConfigurationSerializer
from StiCazzi.env import MONGO_API_URL, MONGO_API_USER, MONGO_API_PWD, MONGO_SERVER_CERTIFICATE, MAX_FILE_SIZE
from . import utils

SESSION_DBG = False
logger = logging.getLogger(__name__)


def authentication(fn):

    def wrapper_fn(*args, **kwargs):

        result = {"success":False, "new_token":"", "code": 401}
        request = args[0]

        if request.content_type == "application/json":
            try:
                i_data = json.loads(request.body)
                username = i_data.get('username', '')
                rosebud_uid = i_data.get('rosebud_uid', '')
                device_id = i_data.get('device_uuid', '')
                app_version = i_data.get('app_version', '')
                device_version = i_data.get('device_version', '')
                device_platform = i_data.get('device_platform', '')
                fcm_token = i_data.get('fcm_token', '')
                logger.debug("Authentication [%s] [%s]" % (request.path, username))
            except ValueError:
                result['message'] = 'Invalid data'
                result['code'] = 400
                return JsonResponse(result, status=result['code'])
        elif request.content_type == "multipart/form-data":
            username = request.POST.get('username', request.POST.get('username2', ''))
            rosebud_uid = request.POST.get('rosebud_uid', '')
            device_id = request.POST.get('device_uuid', '')
            app_version = request.POST.get('app_version', '')
            device_version = request.POST.get('device_version', '')
            device_platform = request.POST.get('device_platform', '')
            logger.debug("Authentication [%s] [%s]" % (request.path, username))
        else:
            result['message'] = 'Invalid data'
            result['code'] = 400
            return JsonResponse(result, status=result['code'])

        users = User.objects.filter(username=username)
        current_user = users.first()
        if not current_user:
            result['code'] = 401
            return JsonResponse(result, status=result['code'])

        uid_ts = None
        rosebud_uid_stored = ''
        user_device=UserDevice.objects.filter(user=current_user, device_id=device_id)
        if user_device:
            rosebud_uid_stored = user_device.first().rosebud_id
            uid_ts = user_device.first().updated

        #logger.debug("="*30)
        #logger.debug(rosebud_uid)
        #logger.debug("="*30)

        if rosebud_uid == rosebud_uid_stored:
            logger.debug("Authentication Successful [%s] [%s]" % (request.path, username))
            result['success'] = True

            #Check if token is expired
            #now = datetime.utcnow()
            #now = now.replace(tzinfo=None)
            now = timezone.now()
            #uid_ts = uid_ts.replace(tzinfo=None)
            time_diff = now - uid_ts
            time_diff_hrs = time_diff.total_seconds() / 3600
            logger.debug("Session time : %1.3f hours" % time_diff_hrs)
            if time_diff_hrs > 1 and request.path == "/refreshtoken":
                new_token = uuid.uuid4()
                current_user.save()
                if user_device:
                    ud = user_device.first()
                    ud.rosebud_id = str(new_token)
                    ud.device_version = device_version
                    ud.device_platform = device_platform
                    ud.app_version = app_version
                    if fcm_token:
                        ud.fcm_token = fcm_token
                    ud.save()
                    result['new_token'] = new_token
                    logger.debug("New token created for user [%s]" % current_user.username)
            result['code'] = 200
            result['payload'] = fn(*args, **kwargs)
        else:
            logger.debug("Authentication Failed [%s] [%s]" % (request.path, username))
            result['payload'] = {}

        return JsonResponse(result, status=result['code'])

    return wrapper_fn


@authentication
def refresh_token(request):
    response = {}
    return response


@authentication
def get_last_commit(request):
    git_folder = '/home/ubuntu/Work/StiCazziD2'
    repo = git.Repo(".")
    if repo:
        response = {'revision': repo.head.commit.name_rev, "message": repo.head.commit.summary}
    else:
        response = {}
    return response


@authentication
def get_random_song(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
    except ValueError:
        response_data['result'] = 'failure'
        response_data['message'] = 'Bad input format'
        response_data['status_code'] = 400

    song_rs = Song.objects.all()
    random_index = randint(0, len(song_rs) - 1)
    song = song_rs[random_index]

    if song:
        lyrics_list = Lyric.objects.all().filter(id_song_id=song.id_song)
        final_list = [{'id':rec.id_lyric, 'text':rec.lyric} for rec in lyrics_list]
        out = {'title':song.title, 'author':song.author, 'spotify': song.spotify, 'youtube': song.youtube, 'deezer': song.deezer, 'lyrics':final_list}
        response_data['message'] = out
    else:
        response_data['message'] = 'song not found'

    return response_data


def login(request):
    """
    Controller:
    """

    response_data = {}
    response_data['result'] = 'success'
    logged = "no"
    try:

        try:
            i_data = json.loads(request.body)
            username = i_data.get('username', '')
            password = i_data.get('password', '')
            device_id = i_data.get('device_uuid', '')
            device_version = i_data.get('device_version', '')
            device_platform = i_data.get('device_platform', '')
            app_version = i_data.get('app_version', '')
            logger.debug("New login have been used")
        except ValueError:
            response_data['message'] = 'Invalid data'

        if not username or not password:
            response_data['result'] = 'failure'
            response_data['payload'] = {"message": "Not valid credentials", 'logged':'no'}
            return JsonResponse(response_data, status=401)


        out = ""
        extra_info = {}
        rosebud_uid = uuid.uuid4()
        users = User.objects.filter(username=username)

        if users:
            pwd_ok = check_password(password, users.first().password)
            out = "User found!"
            if pwd_ok:
                logged = "yes"
                current_user = users.first()
                current_user.save()

                user_device = UserDevice.objects.filter(user=current_user, device_id=device_id)
                if user_device:
                    ud = user_device.first()
                    ud.rosebud_id = str(rosebud_uid)
                    ud.device_version = device_version
                    ud.device_platform = device_platform
                    ud.app_version = app_version
                    ud.save()
                else:
                    user_device = UserDevice(user=current_user,
                        device_id=device_id,
                        rosebud_id=str(rosebud_uid),
                        device_version=device_version,
                        device_platform=device_platform,
                        app_version=app_version)
                    user_device.save()
                extra_info['poweruser'] = current_user.poweruser
                extra_info['geoloc_enabled'] = current_user.geoloc_enabled

        else:
            out = "User not found!"
            logged = "no"

        logger.debug("login result for user " + username + " : " + out)
        response_data['payload'] = {"message":out, 'username':users.first().username, 'logged':logged, 'rosebud_uid': rosebud_uid, 'extra_info': extra_info}

    except Exception as eee:
        response_data['result'] = 'failure'
        response_data['payload'] = {}
        logger.debug(eee)

    if logged == "no":
        response_data['payload'] = {"message": "Not valid credentials", 'logged':'no'}
        return JsonResponse(response_data, status=401)

    return JsonResponse(response_data)


@authentication
def geolocation(request):
    """
    Controller:
    """

    logger.debug("GeoLocation called")

    response = {
            'result':'success',
            'distance': 0,
            'distance_home': 0,
            'location_string': ''
    }
    ret_status = 200

    try:
        logger.debug("New post method used")
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        longitude = i_data.get('longitude', '')
        latitude = i_data.get('latitude', '')
        photo = i_data.get('photo', '')
        action = i_data.get('action', '')
        notification_on = i_data.get('notification_on', False)
        is_home = i_data.get('is_home', False)
    except ValueError as e:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        logger.error(e)
        return response

    logger.debug("Action: %s" % action)
    logger.debug("Notification On: %s" % notification_on)

    if notification_on == "true":
        notification_on = True
    else:
        notification_on = False

    if is_home == "true":
        is_home = True
    else:
        is_home = False

    users = User.objects.filter(username=username)
    loc = Location.objects.filter(user=users[0])

    if action == 'DELETE':
        #DELETE
        logger.debug("DELETE")
        if loc:
            loc[0].delete()
            response['message'] = 'GPS coordinates have been delete from the system for user %s' % username
        else:
            response['message'] = 'GPS coordinates not available for user %s, deletion not needed.' % username
    elif action == 'GET':
        locations = Location.objects.all()
        out = []
        for location in locations:
            out.append({
                'name':location.user.username,
                'latitude':str(location.latitude),
                'longitude':str(location.longitude),
                'photo':location.photo,
                'last_locate':str(location.updated)
            })
        response['body'] = out
        response['message'] = 'Retrieved GPS coordinates for %s user(s)' % len(locations)
    else:
        if latitude and longitude:            #SET COORD
            distance = 0
            distance_home = 0
            location_string = ''
            if loc:

                old_loc = (loc[0].latitude, loc[0].longitude)
                home_loc = (loc[0].home_latitude, loc[0].home_longitude)
                new_loc = (latitude, longitude)
                distance = geodesic(old_loc, new_loc).kilometers
                if loc[0].home_latitude == 0 and loc[0].home_longitude == 0:
                    distance_home = 0
                else:
                    distance_home = geodesic(home_loc, new_loc).kilometers

                ### GeoLocation Info
                geolocator = Nominatim(user_agent="rosebud-application")
                location_info = ''

                try:
                    location_info = geolocator.reverse([latitude, longitude])
                except Exception as e:
                    logger.error("Error during location name retrieval: " + str(e))

                city = 'Ghost Town'
                country = 'Nowhere land'
                county = ''
                if location_info:
                    try:
                        #logger.debug(location_info.raw)
                        city = location_info.raw['address'].get('city','')
                        if not city:
                            city = location_info.raw['address'].get('town','')
                        if not city:
                            city = location_info.raw['address'].get('village','Ghost Town')
                        country = location_info.raw['address'].get('country','')
                        county = location_info.raw['address'].get('county','')
                        location_string = "%s %s (%s)" % (city, county, country)
                        #logger.debug("%s %s %s" % (city, county, country))
                        if county != city:
                            county = "-%s-" % county
                        else:
                            county =''
                    except Exception as e:
                      logger.error(e)
                ### End GeoLocation Info

                logger.debug("Distance %s km." % "{0:.2f}".format(float(distance)))
                logger.debug("Distance from home %s km." % "{0:.2f}".format(float(distance_home)))

                loc[0].latitude = latitude
                loc[0].longitude = longitude
                if is_home:
                    loc[0].home_latitude = latitude
                    loc[0].home_longitude = longitude
                if photo:
                    loc[0].photo = photo
                loc[0].save()

                notif_title = ''
                message = ''
                if notification_on:
                    notif_title = "%s shared his/her current location!" % users[0].username
                    message="%s %s (%s)" % (city, county, country)
                elif float(distance) > 20:
                    notif_title = "%s moved to %s %s (%s)" % (users[0].username, city, county, country)
                    message="As the crow flies: %s km" % "{0:.2f}".format(float(distance))

                #logger.debug(notif_title)

                if notification_on or float(distance) > 20:
                    notification = Notification(
                        type="new_location", \
                        title=notif_title, \
                        message=message, \
                        username=users[0].username)
                    notification.save()

            else:
                if not is_home:
                    location = Location(user=users[0], latitude=latitude, longitude=longitude, photo=photo)
                else:
                    location = Location(user=users[0], latitude=latitude, longitude=longitude, home_latitude=latitude, home_longitude=longitude, photo=photo)
                location.save()
            response['message'] = 'GPS coordinates have been created/updated for user %s' % username
            response['distance'] = "{0:.2f}".format(float(distance))
            response['distance_home'] = "{0:.2f}".format(float(distance_home))
            response['location_string'] = location_string
        else:
            response['result'] = 'failure'
            ret_status = 400

    return response


@authentication
def geolocation2(request):
    """
    Controller:
    """

    response = {'result':'success'}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        action = i_data.get('action', '')
        longitude = i_data.get('longitude', '')
        latitude = i_data.get('latitude', '')
        photo = i_data.get('photo', '')
    except ValueError:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        response['status_code'] = 400
        return response

    users = User.objects.filter(username=username)
    loc = Location.objects.filter(user=users[0])
    response['status_code'] = 200

    if action == 'DELETE':
        response['message'] = 'GPS coordinates not available for user %s, deletion not needed.' % username
        if loc:
            loc[0].delete()
            response['message'] = 'GPS coordinates have been delete from the system for user %s' % username

    elif action == 'GET':
        locations = Location.objects.all()
        out = []
        for location in locations:
            out.append({
                'name':location.user.username,
                'latitude':str(location.latitude),
                'longitude':str(location.longitude),
                'photo':location.photo,
                'last_locate':str(location.updated)
                })
        response['body'] = out
        response['message'] = 'Retrieved GPS coordinates for %s user(s)' % len(locations)

    else:
        if latitude and longitude:            #SET COORD
            if loc:
                loc[0].latitude = latitude
                loc[0].longitude = longitude
                loc[0].save()
            else:
                location = Location(user=users[0], latitude=latitude, longitude=longitude)
                location.save()
            response['message'] = 'GPS coordinates have been created/updated for user %s' % username
        else:
            response['status_code'] = 400

    return response


@authentication
def set_fb_token2(request):
    """
    Controller:
    """
    from types import SimpleNamespace
    logger.debug("Set FB Token 2 called")
    response = {}

    i_data = json.loads(request.body)
    n = SimpleNamespace(**i_data)

    return response


# def check_google(token):
#     """
#     Controller:
#     """

#     out = {"result": False, "info": "Invalid token"}

#     try:
#         if token:
#             # Specify the CLIENT_ID of the app that accesses the backend:
#             idinfo = google_id_token.verify_oauth2_token(token, google_requests.Request())

#             # Or, if multiple clients access the backend server:
#             # idinfo = google_id_token.verify_oauth2_token(token, requests.Request())
#             # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
#             #     raise ValueError('Could not verify audience.')

#             if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
#                 raise ValueError('Wrong issuer.')

#             # If auth request is from a G Suite domain:
#             # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
#             #     raise ValueError('Wrong hosted domain.')

#             # ID token is valid. Get the user's Google Account ID from the decoded token.
#             out['result'] = True
#             out['info'] = idinfo['sub']

#     except ValueError as exception:
#         # Invalid token
#         logger.debug(str(exception))
#         out['info'] = str(exception)

#     return out

# def test_session(request):
#     """
#     Controller:
#     """

#     response = {'result':'success'}

#     try:
#         i_data = json.loads(request.body)
#         #logger.debug("Valid JSON data received.")
#         username = i_data.get('username', '')
#         firebase_id_token = i_data.get('firebase_id_token', '')
#         kanazzi = i_data.get('kanazzi', '')
#     except ValueError:
#         response['result'] = 'failure'
#         response['message'] = 'Bad input format'
#         return JsonResponse(response, status=400)

#     token_check = check_google(firebase_id_token)
#     # user_check = check_session(kanazzi, username, action='test_session', store=True)

#     if not username or not token_check['result']:
#         response['result'] = 'failure'
#         response['message'] = 'Invalid Session: %s' % token_check['info']
#         return JsonResponse(response, status=401)

#     response['message'] = 'Authentication successful! By Google Token: %s' % token_check['info']
#     return JsonResponse(response, status=200)


def get_mongoapi_version():
    """ Get info about mongoapi version"""
    response_data = {}

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getVersion"
    response = requests.get(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return json.loads(response.text)
    else:
        return {}


@authentication
def version(request):
    """
    Controller:
    """
    logger.debug("get version called")
    response = {}

    current_version = get_version()
    mongoapi_version = get_mongoapi_version()
    if mongoapi_version:
        mongoapi_version = mongoapi_version['payload']['version']
    else:
        mongoapi_version = "N/A"

    response['django'] = current_version
    response['mongo'] = mongoapi_version
    return response


@authentication
def get_configs_new(request):
    """ Get Configurations """
    logger.debug("get configurations new called")

    configs = Configuration.objects.all()
    serializer = ConfigurationSerializer(configs, many=True)
    return serializer.data
