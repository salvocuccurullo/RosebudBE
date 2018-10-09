import json, decimal, datetime, operator, base64, os, time, hashlib, urllib
from random import randint
from datetime import date, datetime
from django.core import serializers
from Crypto.Cipher import AES

import requests
from requests.auth import HTTPBasicAuth

from django.http import HttpResponse
from StiCazzi.models import User, Session, Notification
from StiCazzi.controllers import check_session
from StiCazzi.utils import safe_file_name

from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.hashers import *
from django.forms.models import model_to_dict
from django.db.models import Q


def get_random_cover(request):

	response_data = {}

	mongo_api_url = os.environ.get('MONGO_API_URL','')
	mongo_api_user = os.environ.get('COVER_API_USER','')
	mongo_api_pwd = os.environ.get('COVER_API_PW','')
	mongo_server_certificate = os.environ.get('MONGO_SERVER_CERTIFICATE')

	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','').strip()

	if not username or not kanazzi or not check_session(kanazzi, username, action='getRandomCover', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)


	headers = {'Content-Type': 'application/json'}
	mongo_api_url += "/getRandomCover"
	response = requests.post(mongo_api_url, auth=HTTPBasicAuth(mongo_api_user, mongo_api_pwd), verify=mongo_server_certificate, headers=headers)

	status_code = response.status_code
	response_body = response.text
	
	if str(status_code) == "200":
		return HttpResponse(json.dumps(response_body), content_type="application/json")
	else:
		response_body = {"result":"failure", "message":response.text, "status_code":status_code}
		return HttpResponse(json.dumps(response_body), content_type="application/json", status=status_code)


def get_remote_covers(request):

	response_data = {}

	mongo_api_url = os.environ.get('MONGO_API_URL','')
	mongo_api_user = os.environ.get('COVER_API_USER','')
	mongo_api_pwd = os.environ.get('COVER_API_PW','')
	mongo_server_certificate = os.environ.get('MONGO_SERVER_CERTIFICATE')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','').strip()

	if not username or not kanazzi or not check_session(kanazzi, username, action='getRemoteCovers', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)


	headers = {'Content-Type': 'application/json'}
	mongo_api_url += "/getRemoteCovers"
	response = requests.post(mongo_api_url, auth=HTTPBasicAuth(mongo_api_user, mongo_api_pwd), verify=mongo_server_certificate, headers=headers)

	status_code = response.status_code
	response_body = response.text
	
	if str(status_code) == "200":
		return HttpResponse(json.dumps(response_body), content_type="application/json")
	else:
		response_body = {"result":"failure", "message":response.text, "status_code":status_code}
		return HttpResponse(json.dumps(response_body), content_type="application/json", status=status_code)

def get_covers(request):

	response_data = {}

	mongo_api_url = os.environ.get('MONGO_API_URL','')
	mongo_api_user = os.environ.get('COVER_API_USER','')
	mongo_api_pwd = os.environ.get('COVER_API_PW','')
	mongo_server_certificate = os.environ.get('MONGO_SERVER_CERTIFICATE')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','').strip()

	if not username or not kanazzi or not check_session(kanazzi, username, action='getCovers', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)


	headers = {'Content-Type': 'application/json'}
	mongo_api_url += "/getAllCovers"
	response = requests.post(mongo_api_url, auth=HTTPBasicAuth(mongo_api_user, mongo_api_pwd), verify=mongo_server_certificate, headers=headers)

	status_code = response.status_code
	response_body = response.text
	
	if str(status_code) == "200":
		return HttpResponse(json.dumps(response_body), content_type="application/json")
	else:
		response_body = {"result":"failure", "message":response.text, "status_code":status_code}
		return HttpResponse(json.dumps(response_body), content_type="application/json", status=status_code)


def upload_cover(request, safe_file_name, type="poster"):
	print("Finalizing uploaded file saving...")
  
	saving_res = True
	response_data = {'result':'success'}
	MAX_FILE_SIZE = os.environ['UPLOAD_MAX_SIZE']
	
	if request.method == 'POST':
		f = request.FILES.get('pic','')
		if (f):
			print("File Name: " + str(f.name))           # Gives name
			print("Content Type:" + str(f.content_type)) # Gives Content type text/html etc
			print("File size: " + str(f.size))           # Gives file's size in byte
			
			if int(f.size) > int(MAX_FILE_SIZE):
				response_data = {'result':'failure', 'message':'file size is exceeding the maximum size allowed'}
			else:
				saving_res = handle_uploaded_file(f, safe_file_name, type)
		else:
			response_data = {'result':'failure', 'message':'invalid request'}
	
	if not saving_res:
		response_data = {'result':'failure', 'message':'error during saving file on remote server'}
		
	return response_data


def get_covers_stats(request):

	response_data = {}

	mongo_api_url = os.environ.get('MONGO_API_URL','')
	mongo_api_user = os.environ.get('COVER_API_USER','')
	mongo_api_pwd = os.environ.get('COVER_API_PW','')
	mongo_server_certificate = os.environ.get('MONGO_SERVER_CERTIFICATE')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','').strip()

	if not username or not kanazzi or not check_session(kanazzi, username, action='getCovers', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)


	headers = {'Content-Type': 'application/json'}
	mongo_api_url += "/getStats"
	response = requests.post(mongo_api_url, auth=HTTPBasicAuth(mongo_api_user, mongo_api_pwd), verify=mongo_server_certificate, headers=headers)

	status_code = response.status_code
	response_body = response.text

	if str(status_code) == "200":
		return HttpResponse(json.dumps(response_body), content_type="application/json")
	else:
		response_body = {"result":"failure", "message":response.text, "status_code":status_code}

	return HttpResponse(json.dumps(response_body), content_type="application/json", status=status_code) 


def save_cover(request):

	response_data = {}

	mongo_api_url = os.environ.get('MONGO_API_URL','')
	mongo_api_user = os.environ.get('COVER_API_USER','')
	mongo_api_pwd = os.environ.get('COVER_API_PW','')
	mongo_server_certificate = os.environ.get('MONGO_SERVER_CERTIFICATE')

	title = request.POST.get('title','')
	author = request.POST.get('author','')
	year = request.POST.get('year','0')
	id = request.POST.get('id','')
	username = request.POST.get('username2','')
	kanazzi = request.POST.get('kanazzi','').strip()
	f = request.FILES.get('pic','')
	cover_name = ''
	upload_file_res = {} 

	if not username or not kanazzi or not check_session(kanazzi, username, action='uploadcover', store=True):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

	print("Cover Upload")
	print(title.encode('utf-8'))
	print(author.encode('utf-8'))
	print(year)
	if id:
		print("object id received: " + id)
		print("going to update record....")
	print("============")
	
	upload_file_res = {}
	if f:
		print("A file has been uploaded... " + f.name)
		temp_f_name = title + '_' + f.name
		cover_name = safe_file_name(temp_f_name, f.content_type)
		upload_file_res = upload_cover(request, cover_name, type="cover")

	upload_res = upload_file_res.get('result','failure')
	if upload_res == 'failure' and cover_name != "" and id != "":
		response_data = upload_file_res
		return HttpResponse(json.dumps(response_data), content_type="application/json")

	#title = title.encode('utf-8')
	#author = author.encode('utf-8')
	
	'''
	mongo_api_url += "/createCover?fileName=%s&coverName=%s&author=%s&year=%s" % (cover_name, title, author, year)
	response = requests.get(mongo_api_url, auth=HTTPBasicAuth(mongo_api_user, mongo_api_pwd), verify=False)
	'''
	
	headers = {'Content-Type': 'application/json'}
	payload = {"name":title, "author":author, "year":year, "username":username}
	
	if id:
		payload.update({'id':id})
	if cover_name:
		payload.update({'fileName':cover_name})

	payload = json.dumps(payload)
	mongo_api_url += "/createCover2"
	response = requests.post(mongo_api_url, auth=HTTPBasicAuth(mongo_api_user, mongo_api_pwd), verify=mongo_server_certificate, headers=headers, data=payload)

	status_code = response.status_code
	response_body = response.text
	print(response_body)
	
	if str(status_code) == "200":
		t = urllib.parse.unquote(title)
		a = urllib.parse.unquote(author)
		n = Notification(type="new_cover", title="%s has just added a new cover" %username, message="%s - %s" % (t,a), username=username)
		n.save()
	else:
		response_body = {"result":"failure", "message":response.text, "status_code":status_code}
		return HttpResponse(json.dumps(response_body), content_type="application/json", status=status_code)
	
	print("**************")
	print(mongo_api_url)
	print(status_code)
	print(payload)
	print("**************")

	return HttpResponse(json.dumps(response_body), content_type="application/json")


def handle_uploaded_file(f, safe_file_name, type="poster"):
	
	if type == "poster":
		path = os.environ.get('UPLOAD_SAVE_PATH','')
	else:
		path = os.environ.get('UPLOAD_SAVE_PATH_COVER','')
		
	if not path:
		print("Base path for saving uploaded file is not valid: %s" % path)
		return False

	final_full_path = path + safe_file_name
	try:
		print("Saving uploaded file to %s ..." % final_full_path)
		with open(final_full_path, 'wb+') as destination:
			for chunk in f.chunks():
				destination.write(chunk)
	except:
		return False
	
	return True
