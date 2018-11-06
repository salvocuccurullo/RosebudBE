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
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    if not username or not kanazzi or not check_session(kanazzi, username, action='getRandomCover', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getRandomCover"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)


def get_remote_covers(request):
    """ Get all covers not stored in the app """
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    if not username or not kanazzi or not check_session(kanazzi, username, action='getRemoteCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getRemoteCovers"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)


def get_covers(request):
    """ Get all covers from API """
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    if not username or not kanazzi or not check_session(kanazzi, username, action='getCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getAllCovers"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

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
    logger.debug("Get Covers Stats called")
    response_data = {}

    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '').strip()

    if not username or not check_session(kanazzi, username, action='getCovers', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getStats"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)

def get_covers_stats_2(request):
    """ Get covers statistics from API """
    logger.debug("Get Covers Stats 2 called")
    response_data = {}

    username = request.POST.get('username', '')
    firebase_id_token = request.POST.get('firebase_id_token', '')
    kanazzi = request.POST.get('kanazzi', '').strip()
    token_check = check_google(firebase_id_token)

    if not username or not kanazzi or not token_check['result']:
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session: %s' % token_check['info']
        return JsonResponse(response_data, status=401)

    headers = {'Content-Type': 'application/json'}
    mongo_final_url = MONGO_API_URL + "/getStats"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers)

    status_code = response.status_code
    response_body = response.text

    if str(status_code) == "200":
        return JsonResponse(response_body, safe=False)

    response_body = {"result": "failure", "message": response.text, "status_code": status_code}
    return JsonResponse(response_body, status=status_code, safe=False)

def save_cover(request):
    """ Save a new cover """
    response_data = {}

    title = request.POST.get('title', '')
    author = request.POST.get('author', '')
    year = request.POST.get('year', '0')
    id_cover = request.POST.get('id', '')
    username = request.POST.get('username2', '')
    kanazzi = request.POST.get('kanazzi', '').strip()
    cover_file = request.FILES.get('pic', '')
    cover_name = ''
    upload_file_res = {}

    if not username or not kanazzi or not check_session(kanazzi, username, action='uploadcover', store=True):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    logger.debug("Cover Upload: %s - %s - %s" % (title.encode('utf-8'), author.encode('utf-8'), str(year)))

    if id_cover:
        logger.debug("object id received: %s Going to update record...." % id_cover)

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

    payload = json.dumps(payload)
    mongo_final_url = MONGO_API_URL + "/createCover2"
    response = requests.post(mongo_final_url, auth=HTTPBasicAuth(MONGO_API_USER, MONGO_API_PWD), verify=MONGO_SERVER_CERTIFICATE, headers=headers, data=payload)

    status_code = response.status_code
    response_body = response.text

    logger.debug("**************")
    logger.debug("%s - %s - %s ==> %s" % (mongo_final_url, str(status_code), str(payload), response_body))
    logger.debug("**************")

    if str(status_code) == "200":
        title = urllib.parse.unquote(title)
        author = urllib.parse.unquote(author)
        notif = Notification(type="new_cover", title="%s has just added a new cover" % username, message="%s - %s" % (title, author), username=username)
        notif.save()
    else:
        response_body = {"result": "failure", "message": response.text, "status_code": status_code}
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
