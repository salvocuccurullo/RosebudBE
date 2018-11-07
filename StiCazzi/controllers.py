"""
 Controller: login and generic
"""

import json
import base64
import os
import logging

from random import randint
from datetime import datetime
from Crypto.Cipher import AES

import firebase_admin
from firebase_admin import credentials, auth

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.core import serializers

from StiCazzi.models import Pesata, Soggetto, Song, Lyric, Movie, User, Session, Location
from . import utils

SESSION_DBG = True
logger = logging.getLogger(__name__)

def get_demo_json(request):
    """
    Controller:
    """

    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = 'hello world!'

    return JsonResponse(response_data)

def get_random_song(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '')

    if not username and not kanazzi:
        username = request.GET.get('username', '')
        kanazzi = request.GET.get('kanazzi', '')
        logger.debug("A client is using a deprecated GET method for get random song")
    else:
        # CHECK SESSION - SOFT VERSION - NO SAVE ON DB
        if not check_session(kanazzi, username, action='getRandomSong', store=False):
            response_data['result'] = 'failure'
            response_data['message'] = 'Invalid Session'
            return JsonResponse(response_data, status=401)

        # END CHECK SESSION

    song_rs = Song.objects.all()
    random_index = randint(0, len(song_rs) - 1)
    song = song_rs[random_index]

    if song:
        lyrics_list = Lyric.objects.all().filter(id_song_id=song.id_song)
        final_list = [{'id':rec.id_lyric, 'text':rec.lyric} for rec in lyrics_list]
        out = {'title':song.title, 'author':song.author, 'lyrics':final_list}
        response_data['message'] = out
    else:
        response_data['message'] = 'song not found'
        return JsonResponse(response_data)

    return JsonResponse(response_data)


def get_songs(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'
    response_data['payload'] = serializers.serialize("json", Song.objects.all())

    return JsonResponse(response_data)


def get_lyrics_by_song(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'

    try:
        int(request.GET['id_song'])
    except ValueError:
        response_data['result'] = 'error'
        response_data['message'] = 'not valid id'
        return JsonResponse(response_data)

    songs = Song.objects.filter(id_song=request.GET['id_song'])

    if songs:
        song = songs[0]
        lyrics_list = Lyric.objects.all().filter(id_song_id=song.id_song)
        final_list = [{'id':rec.id_lyric, 'text':rec.lyric} for rec in lyrics_list]
        out = {'title':song.title, 'author':song.author, 'lyrics':final_list}
        response_data['message'] = json.dumps(out)
    else:
        response_data['message'] = 'song not found'

    return JsonResponse(response_data)

def get_movies(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'
    response_data['payload'] = serializers.serialize("json", Movie.objects.all())

    return JsonResponse(response_data)


def get_pesate_by_soggetto(request, id_soggetto):
    """
    Controller:
    """

    response_data = {}
    soggetti = Soggetto.objects.filter(id_soggetto=id_soggetto)

    if soggetti:
        soggetto = soggetti[0]
        lista_pesi = Pesata.objects.filter(id_soggetto=id_soggetto)
        peso_list = []
        for peso in lista_pesi:
            peso_diz = {'data':peso.data.strftime("%d/%m/%y"), 'peso':peso.peso}
            peso_diz = utils.decimal_dumps(peso_diz)
            peso_list.append(peso_diz)
        response_data['message'] = {'nome': soggetto.nome,
                                    'cognome': soggetto.cognome,
                                    'pesate':peso_list}
    else:
        response_data['message'] = {}
    #peso_list = json.dumps(peso_list)

    response_data['result'] = 'success'

    return JsonResponse(response_data)

def get_all_pesate(request):
    """
    Controller:
    """

    out = {}
    soggetti = Soggetto.objects.values_list('id_soggetto', 'nome')
    for soggetto in soggetti:
        pesate = Pesata.objects.filter(id_soggetto=soggetto)
        peso_list = []
        for peso in pesate:
            peso_diz = {'data':peso.data.strftime("%Y/%m/%d"), 'peso':peso.peso}
            peso_diz = utils.decimal_dumps(peso_diz)
            peso_list.append(peso_diz)

        out[soggetto[0]] = {}
        out[soggetto[0]]['nome'] = soggetto[1]
        out[soggetto[0]]['pesate'] = peso_list

    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = out

    return JsonResponse(response_data)

def get_sum_by_month(request):
    """
    Controller:
    """

    out = {}
    soggetti = Soggetto.objects.values_list('id_soggetto', 'nome')
    for soggetto in soggetti:
        pesate = Pesata.objects.filter(id_soggetto=soggetto[0]) #.order_by('data')
        peso_list = []
        mesi_diz = {}
        for peso in pesate:
            mese_anno = peso.data.strftime("%Y%m")
            if mese_anno not in mesi_diz:
                mesi_diz[mese_anno] = {'pesi_mese':[]}
            mesi_diz[mese_anno]['pesi_mese'].append(peso.peso)
            mesi_diz[mese_anno]['last_data'] = peso.data.strftime("%Y/%m/%d")

        pesate = list(mesi_diz.keys())
        pesate.sort()

        for mese_anno in pesate:
            cum_peso = mesi_diz[mese_anno]['pesi_mese'][0] - mesi_diz[mese_anno]['pesi_mese'][-1]
            peso_diz = {'data':mesi_diz[mese_anno]['last_data'], 'peso':cum_peso}
            peso_diz = utils.decimal_dumps(peso_diz)
            peso_list.append(peso_diz)

        out[soggetto[0]] = {}
        out[soggetto[0]]['nome'] = soggetto[1]
        out[soggetto[0]]['pesate'] = peso_list

    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = out

    return JsonResponse(response_data)

def check_session(session_id, username, action='', store=False):
    """
    Controller:
    """

    if not username or not session_id:
        return False

    logger.debug("Classic check session starting")
    session_id = session_id.strip()
    sessions = Session.objects.filter(session_string=session_id)
    if sessions:
        #print "session already exists"
        return False

    #Semantic check
    decryption_suite = AES.new(os.environ['OPENSHIFT_DUMMY_KEY'], AES.MODE_ECB, '')
    plain_text = decryption_suite.decrypt(base64.b64decode(session_id))
    try:
        #print session_id.strip()
        plain_text = plain_text.strip()
        session_dt = datetime.strptime(str(plain_text.decode("utf-8")), "%Y_%m_%d_%H_%M_%S_%f")
        if SESSION_DBG:
            logger.debug("Valid session id for user %s", username)
        now = datetime.now()
        time_diff = now - session_dt

        if time_diff.days > 90:
            if SESSION_DBG:
                logger.debug("Session expired : %s days", str(time_diff.days))
            return False

        if SESSION_DBG:
            logger.debug("Session not expired : %s days", str(time_diff.days))

    except Exception as exception:
        if SESSION_DBG:
            logger.debug(exception)
            logger.debug("Not valid session id")
        return False

    if store:
        session = Session(session_string=session_id, username=username, action=action)
        session.save()

    return True


def login(request):
    """
    Controller:
    """

    response_data = {}
    response_data['result'] = 'success'
    try:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username or not password:
            response_data['result'] = 'failure'
            response_data['payload'] = {"message": "Not valid credentials", 'logged':'no'}
            return JsonResponse(response_data, status=401)

        decryption_suite = AES.new(os.environ['OPENSHIFT_DUMMY_KEY'], AES.MODE_ECB, '')
        plain_text = decryption_suite.decrypt(base64.b64decode(password))

        out = ""
        logged = "no"
        users = User.objects.filter(username=username)

        if users:
            plain_text = plain_text.decode('utf-8').strip()
            pwd_ok = check_password(plain_text, users[0].password)
            out = "User found!"
            if pwd_ok:
                logged = "yes"
        else:
            out = "User not found!"
            logged = "no"

        logger.debug("login result for user " + username + " : " + out)
        response_data['payload'] = {"message":out, 'username':username, 'logged':logged}

    except Exception as eee:
        response_data['result'] = 'failure'
        response_data['payload'] = {}
        logger.debug(eee)

    if logged == "no":
        response_data['payload'] = {"message": "Not valid credentials", 'logged':'no'}
        return JsonResponse(response_data, status=401)

    return JsonResponse(response_data)


def login2(request):
    """
    Controller:
    """

    response = {'result':'success'}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        email = i_data.get('email', '')
        firebase_id_token = i_data.get('firebase_id_token', '')
        app_version = i_data.get('app_version', '')
        fcm_token = i_data.get('fcm_token', '')
    except ValueError:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    token_check = check_google(firebase_id_token)

    if not username or not token_check['result']:
        response['result'] = 'failure'
        response['payload'] = {"message": "Not valid credentials", 'logged':'no'}
        return JsonResponse(response, status=401)

    user = User.objects.filter(username=username).first()

    if user:
        user.email = email
        user.firebase_id_token = firebase_id_token
        user.save()
        logger.debug("Existing user logged in: %s", email)
    else:
        u = User(
            username=username, \
            email=email, \
            firebase_id_token=firebase_id_token, \
            app_version=app_version, \
            password='', \
            firebase_uid='', \
            fcm_token=fcm_token \
        )
        u.save()

        logger.debug("New user logged in: %s", email)
    response['payload'] = {"message":"welcome", 'username':username, 'logged':True}

    return JsonResponse(response)


def geolocation(request):
    """
    Controller:
    """

    response = {'result':'success'}
    username = request.POST.get('username', '')
    longitude = request.POST.get('longitude', '')
    latitude = request.POST.get('latitude', '')
    photo = request.POST.get('photo', '')
    action = request.POST.get('action', '')
    kanazzi = request.POST.get('kanazzi', '').strip()
    ret_status = 200

    if not check_session(kanazzi, username, action='geolocation', store=True):
        response['result'] = 'failure'
        response['message'] = 'Invalid Session'
        return JsonResponse(response, status=401)

    if not action or action not in ('GET', 'SET', 'DELETE'):
        response = {'result':'failure'}
        return JsonResponse(response, status=400)

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
            if loc:
                loc[0].latitude = latitude
                loc[0].longitude = longitude
                if photo:
                    loc[0].photo = photo
                loc[0].save()
            else:
                location = Location(user=users[0], latitude=latitude, longitude=longitude, photo=photo)
                location.save()
            response['message'] = 'GPS coordinates have been created/updated for user %s' % username
        else:
            response['result'] = 'failure'
            ret_status = 400

    return JsonResponse(response, status=ret_status)


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
        firebase_id_token = i_data.get('firebase_id_token', '')
        kanazzi = i_data.get('kanazzi', '')
    except ValueError:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    # logger.debug("Checking firebase id token.... Result: " + str(check_fb_token_local(firebase_id_token)))

    if not check_session(kanazzi, username, action='geolocation2', store=True):
        response['result'] = 'failure'
        response['message'] = 'Invalid Session'
        return JsonResponse(response, status=401)

    if not action or action not in ('GET', 'SET', 'DELETE'):
        response = {'result':'failure'}
        return JsonResponse(response, status=400)

    users = User.objects.filter(username=username)
    loc = Location.objects.filter(user=users[0])
    status_code = 200

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
            status_code = 400

    return JsonResponse(response, status=status_code)

def set_fb_token(request):
    """
    Controller:
    """

    response = {'result':'success'}

    # logger.debug(" ====== request info =====")
    # logger.debug(request.method)
    # logger.debug(request.content_type)
    # logger.debug(" =========================")

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        token = i_data.get('token', '')
        id_token = i_data.get('id_token', '')
        app_version = i_data.get('app_version', '')
    except ValueError:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    if username:
        users = User.objects.filter(username=username)
        if users:
            user = users[0]
            user.app_version = app_version
            if token:
                user.fcm_token = token
            if id_token:
                user.firebase_id_token = id_token
            user.save()
            return JsonResponse(response, status=200)

    response['result'] = 'failure'
    return JsonResponse(response, status=400)


def check_fb_token(request):
    """
    Controller:
    """

    response = {"result":"success", "message":""}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        if SESSION_DBG:
            logger.debug('Starting session check for user %s', username)


        #Google Initializazion
        google_account_file = os.environ.get('GOOGLE_JSON', '')
        if not google_account_file:
            raise ValueError('Google JSON account file not found.')

        if not firebase_admin._apps:
            cred = credentials.Certificate(google_account_file)
            default_app = firebase_admin.initialize_app(cred)

        #Retrieving id_token from DB
        users = User.objects.filter(username=username)
        if not users:
            raise ValueError('User not found.')
        user = users[0]
        id_token = user.firebase_id_token
        if not id_token:
            raise ValueError('idToken is empty!')

        #Verifying id token
        decoded_token = auth.verify_id_token(id_token)

        response["message"] = "Firebase idToken successulfy verified"
        response["payload"] = {"firebase_id_token":id_token}

    except Exception as exception:
        logger.debug(exception)
        if 'Token expired' in str(exception):
            response = {"result":"failure", "message":"token expired"}
            return JsonResponse(response, status=401)

        response = {"result":"failure", "message":str(exception)}
        return JsonResponse(response, status=500)


    return JsonResponse(response, status=200)


def check_fb_token_local(id_token):
    """
    Controller:
    """

    response = False

    try:
        if SESSION_DBG:
            logger.debug('Starting firebase id token check...')

        #Google Initializazion
        google_account_file = os.environ.get('GOOGLE_JSON', '')
        if not google_account_file:
            raise ValueError('Google JSON account file not found.')

        if not firebase_admin._apps:
            cred = credentials.Certificate(google_account_file)
            default_app = firebase_admin.initialize_app(cred)

        #Verifying id token
        decoded_token = auth.verify_id_token(id_token)

        response = True

    except Exception as exception:
        logger.debug(str(exception))

    return response

def check_google(token):
    """
    Controller:
    """

    out = {"result": False, "info": "Invalid token"}

    try:
        if token:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = google_id_token.verify_oauth2_token(token, google_requests.Request())

            # Or, if multiple clients access the backend server:
            # idinfo = google_id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            out['result'] = True
            out['info'] = idinfo['sub']

    except ValueError as exception:
        # Invalid token
        logger.debug(str(exception))
        out['info'] = str(exception)
        
    return out

def test_session(request):
    """
    Controller:
    """

    response = {'result':'success'}

    try:
        i_data = json.loads(request.body)
        logger.debug("Valid JSON data received.")
        username = i_data.get('username', '')
        firebase_id_token = i_data.get('firebase_id_token', '')
        kanazzi = i_data.get('kanazzi', '')
    except ValueError:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    token_check = check_google(firebase_id_token)
    # user_check = check_session(kanazzi, username, action='test_session', store=True)

    if not username or not token_check['result']:
        response['result'] = 'failure'
        response['message'] = 'Invalid Session: %s' % token_check['info']
        return JsonResponse(response, status=401)

    response['message'] = 'Authentication successful! By Google Token: %s' % token_check['info']
    return JsonResponse(response, status=200)
