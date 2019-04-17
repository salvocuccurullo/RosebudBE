"""
    iCarusi BE - Covers Controller
"""

import os
import urllib
import json
import logging

import requests
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse

from StiCazzi.models import Notification
from StiCazzi.controllers import check_session, check_google
from StiCazzi.utils import safe_file_name

MONGO_API_URL = os.environ.get('MONGO_API_URL', '')
MONGO_API_USER = os.environ.get('COVER_API_USER', '')
MONGO_API_PWD = os.environ.get('COVER_API_PW', '')
MONGO_SERVER_CERTIFICATE = os.environ.get('MONGO_SERVER_CERTIFICATE')
MAX_FILE_SIZE = os.environ.get('UPLOAD_MAX_SIZE', 512000)
logger = logging.getLogger(__name__)

def get_random_cover(request):
    """ Get a random cover from API """
    logger.debug("get_random_cover called")
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    if not username or not kanazzi or not check_session(kanazzi, username, action='getRandomCover', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getRandomCover"
    response = requests.get(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)


def get_remote_covers(request):
    """ Get all covers not stored in the app """
    logger.debug("get_remote_covers called")
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    if not username or not kanazzi or not check_session(kanazzi, username, action='getRemoteCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getRemoteCovers"
    response = requests.get(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)


def spotify_auth(request):
    logger.debug("Spotify Auth Called")
    response_data = {}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        kanazzi = i_data.get('kanazzi', '')
        album_url = i_data.get('album_url', '')
        query = i_data.get('query', '')
        search_type = i_data.get('search_type', '')
    except ValueError:
        response_data['result'] = 'failure'
        response_data['message'] = 'Bad input format'
        return JsonResponse(response_data, status=400)
   
    #logger.debug("%s - %s" % (username, kanazzi))
    logger.debug("%s - %s - %s" % (album_url, search_type, query))
    
    if not (album_url or (query and search_type)):
        response_data['result'] = 'failure'
        response_data['message'] = 'Unprocessable Entity: missing parameter'
        return JsonResponse(response_data, status=422)
    
    if not username or not kanazzi or not check_session(kanazzi, username, action='spotifyAuthorization', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)
    
    expected_base_url = ("https://open.spotify.com", "https://api.spotify.com")

    if album_url and not album_url.startswith(expected_base_url):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Spotify URL'
        return JsonResponse(response_data, status=400)
    
    client_info = {
          "grant_type":    "authorization_code",
          "response_type":  "code",
          "redirect_uri":  os.environ.get('SPOTIPY_REDIRECT_URI',''),
          "client_secret": os.environ.get('SPOTIPY_CLIENT_SECRET',''),
          "client_id":     os.environ.get('SPOTIPY_CLIENT_ID','')
    }
    spotify_auth_url = "https://accounts.spotify.com/api/token"
    payload = {"grant_type": "client_credentials"}
    res = requests.post(spotify_auth_url, auth=(os.environ.get('SPOTIPY_CLIENT_ID',''),os.environ.get('SPOTIPY_CLIENT_SECRET','')), data=payload)

    return {"result": res.text, "status_code": res.status_code, "search_type": search_type, "album_url": album_url, "query": query}


def spotify(request):
    """ Get album info from spotify """
   
    logger.debug("Spotify Album Called")
    response_data = {}
    
    spotify_pre_auth = spotify_auth(request)
    if type(spotify_pre_auth) is JsonResponse:
        return spotify_pre_auth

    response = spotify_pre_auth.get('result','')
    album_url = spotify_pre_auth.get('album_url','')
    response_code=spotify_pre_auth.get('status_code','')

    if response_code == 200:
        auth_data = json.loads(response)
        access_token = auth_data['access_token']

        headers = {"Authorization": "Bearer %s" % access_token}
        album_url = "https://api.spotify.com/v1/albums/" + album_url.split("/")[-1]
        logger.debug("Spotify get album: %s" % album_url)
        res = requests.get(album_url, headers=headers)
        if res.status_code == 200:
            album = json.loads(res.text)
            logger.debug("Found on spotify the album: %(name)s" % album)
            return JsonResponse(res.text, status=res.status_code, safe=False)
        else:
            response = res.text
            response_code = res.status_code
    response_body = {"result": "failure", "message": "Spotify album failed. Check the url or the connections", "status_code": response_code}
    return JsonResponse(response_body, status=response_code, safe=False)


def spotify_search(request):
    """ Get album info from spotify """
   
    logger.debug("Spotify Search Called")
    response_data = {}
   
    spotify_pre_auth = spotify_auth(request)
    if type(spotify_pre_auth) is JsonResponse:
        return spotify_pre_auth

    response = spotify_pre_auth.get('result','')
    query = spotify_pre_auth.get('query','')
    search_type = spotify_pre_auth.get('search_type','')
    response_code=spotify_pre_auth.get('status_code','')

    if response_code == 200:
        auth_data = json.loads(response)
        access_token = auth_data['access_token']
        headers = {"Authorization": "Bearer %s" % access_token}
        res = requests.get("https://api.spotify.com/v1/search?q=%s&type=%s" % (query, search_type), headers=headers)
        if res.status_code == 200:
            result = json.loads(res.text)
            data_out = []
            for track in result['tracks']['items']:
                album = {"name": track['album']['name'], "author":track['artists'][0]['name'], "url":track['album']['href'], "tracks_num": track['album']['total_tracks'], 'year': track['album']['release_date'][:4]}
                if album not in data_out:
                    data_out.append(album)
            return JsonResponse({"result":"success", "payload":data_out}, status=res.status_code, safe=False)
        else:
            response = res.text
            response_code = res.status_code
    response_body = {"result": "failure", "message": "Spotify album failed. Check the url or the connections", "status_code": response_code}
    return JsonResponse(response_body, status=response_code, safe=False)




def get_covers(request):
    """ Get all covers from API """
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    #backward compatibility - will be removed soon
    if not username:
    
        try:
            i_data = json.loads(request.body)
            username = i_data.get('username', '')
            kanazzi = i_data.get('kanazzi', '')
        except ValueError:
            response_data['result'] = 'failure'
            response_data['message'] = 'Bad input format'
            return JsonResponse(response_data, status=400)

    if not username or not kanazzi or not check_session(kanazzi, username, action='getCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    #logger.debug(kanazzi)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getAllCovers"
    response = requests.get(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)


def upload_cover(request, safe_fname, cover_type="poster"):
    """ Wrapper for handle_uploaded_file """
    logger.debug("Finalizing uploaded file saving...")

    saving_res = True
    response_data = {'result': 'success'}

    if request.method == 'POST':
        cover_file = request.FILES.get('pic', '')
        if cover_file:
            logger.debug("File Name: " + str(cover_file.name))            # Gives name
            logger.debug("Content Type:" + str(cover_file.content_type))  # Gives Content type text/html etc
            logger.debug("File size: " + str(cover_file.size))            # Gives file's size in byte

            if int(cover_file.size) > int(MAX_FILE_SIZE):
                response_data = {'result': 'failure', 'message': 'file size is exceeding the maximum size allowed'}
            else:
                saving_res = handle_uploaded_file(cover_file, safe_fname, cover_type)
        else:
            response_data = {'result': 'failure', 'message': 'invalid request'}

    if not saving_res:
        response_data = {'result': 'failure', 'message': 'error during saving file on remote server'}

    return response_data


def get_covers_stats(request):
    """ Get covers statistics from API """
    logger.debug("get_covers_stats called")
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    #backward compatibility - will be removed soon
    if not username:

        try:
            i_data = json.loads(request.body)
            username = i_data.get('username', '')
            kanazzi = i_data.get('kanazzi', '')
        except ValueError:
            response_data['result'] = 'failure'
            response_data['message'] = 'Bad input format'
            return JsonResponse(response_data, status=400)

    if not username or not check_session(kanazzi, username, action='getCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getStats"
    response = requests.get(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)

def get_covers_stats_2(request):
    """ Get covers statistics from API """
    logger.debug("get_covers_stats_2 called")
    response_data = {}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        firebase_id_token = i_data.get('firebase_id_token', '')
    except ValueError:
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    token_check = check_google(firebase_id_token)

    if not username or not token_check['result']:
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session: %s' % token_check['info']
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getStats"
    response = requests.get(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)

def save_cover(request):
    """ Save a new cover """
    logger.debug("save_cover called")
    response_data = {}

    title = request.POST.get('title', '')
    author = request.POST.get('author', '')
    year = request.POST.get('year', '0')
    id_cover = request.POST.get('id', '')
    username = request.POST.get('username2', '')
    kanazzi = request.POST.get('kanazzi', '').strip()
    cover_file = request.FILES.get('pic', '')
    spoti_img_url = request.POST.get('spoti_img_url', '')
    spotify_api_url = request.POST.get('spotify_api_url', '')
    cover_name = ''
    upload_file_res = {}

    #logger.debug("%s - %s",username,kanazzi)

    if not username or not kanazzi or not check_session(kanazzi, username, action='uploadcover', store=True):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    logger.debug("Cover Upload: %s - %s - %s" % (title.encode('utf-8'), author.encode('utf-8'), str(year)))

    if id_cover:
        logger.debug("object id received: %s Going to update record...." % id_cover)

    if not spoti_img_url:
        upload_file_res = {}
        if cover_file:
            logger.debug("A file has been uploaded... " + cover_file.name)
            temp_f_name = title + '_' + cover_file.name
            cover_name = safe_file_name(temp_f_name, cover_file.content_type)
            upload_file_res = upload_cover(request, cover_name, cover_type="cover")

        upload_res = upload_file_res.get('result', 'failure')
        if upload_res == 'failure' and cover_name != "" and id_cover != "":
            response_data = upload_file_res
            return JsonResponse(response_data)

    headers = {'Content-Type': 'application/json'}
    payload = {"name": title, "author": author, "year": year, "username": username}

    if id_cover:
        payload.update({'id': id_cover})
    if cover_name:
        payload.update({'fileName': cover_name})
    if spoti_img_url:
        payload.update({'fileName': spoti_img_url})
    if spotify_api_url:
        payload.update({'spotifyUrl': spotify_api_url})

    payload = json.dumps(payload)
    mongo_final_url = MONGO_API_URL + "/createCover2"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers, data=payload)

    status_code = response.status_code
    response_body = response.text

    logger.debug("**************")
    logger.debug("%s - %s - %s ==> %s" % (mongo_final_url, str(status_code), str(payload), response_body))
    logger.debug("**************")

    if str(status_code) == "200" and json.loads(response_body)['result'] != 'failure':
        title = urllib.parse.unquote(title)
        author = urllib.parse.unquote(author)
        notif = Notification(type="new_cover", title="%s has just added a new cover" % username, message="%s - %s" % (title, author), username=username)
        if not id_cover:    #do not send notification for cover editing...
            notif.save()
    else:
        response_body = {"result": "failure", "message": json.loads(response.text)['message'], "status_code": str(status_code)}
        return JsonResponse(response_body, status=status_code, safe=False)

    return JsonResponse(response_body, safe=False)


def handle_uploaded_file(up_file, safe_fname, cover_type="poster"):
    """ Write uploaded file on disk """
    if cover_type == "poster":
        path = os.environ.get('UPLOAD_SAVE_PATH', '')
    else:
        path = os.environ.get('UPLOAD_SAVE_PATH_COVER', '')

    if not path:
        logger.debug("Base path for saving uploaded file is not valid: %s" % path)
        return False

    final_full_path = path + safe_fname
    try:
        logger.debug("Saving uploaded file to %s ..." % final_full_path)
        with open(final_full_path, 'wb+') as destination:
            for chunk in up_file.chunks():
                destination.write(chunk)
    except IOError:
        return False

    return True


def get_covers_by_search(request):
    """ Search covers from API """
    logger.debug("Entering search covers by query")
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    #backward compatibility - will be removed soon
    if not username:

        try:
            i_data = json.loads(request.body)
            username = i_data.get('username', '')
            kanazzi = i_data.get('kanazzi', '')
            search = i_data.get('search', '')
        except ValueError:
            response_data['result'] = 'failure'
            response_data['message'] = 'Bad input format'
            return JsonResponse(response_data, status=400)

    if not username or not kanazzi or not check_session(kanazzi, username, action='searchCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    logger.debug("Searching covers by query: %s" % search)

    headers = {'Content-Type': 'application/json'}
    payload = {'search': search}
    mongo_final_url = MONGO_API_URL + "/searchCovers?search=%s" % search
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers, data=payload)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)
