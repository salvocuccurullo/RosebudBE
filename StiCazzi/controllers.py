import json, decimal, datetime, operator, base64, os, time, hashlib
from random import randint
from datetime import date, datetime
from django.core import serializers
from Crypto.Cipher import AES

import requests
from requests.auth import HTTPBasicAuth

import firebase_admin
from firebase_admin import credentials,auth

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from django.http import HttpResponse
from StiCazzi.models import Pesata, Soggetto, Song, Lyric, Movie, TvShow, User, Minchiate, TvShowVote, Session, Notification, Location, Catalogue
from StiCazzi.utils import safe_file_name
from . import utils

from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.hashers import *
from django.db.models import Q

def get_demo_json(request):
	
	s = Soggetto.objects.all()
	response_data = {}
	response_data['result'] = 'success'
	response_data['message'] = ''

	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_random_song(request):

	response_data = {}
	response_data['result'] = 'success'

	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')
 
	if not username and not kanazzi:
		username = request.GET.get('username','')
		kanazzi = request.GET.get('kanazzi','')
		print("A client is using a deprecated GET method for get random song")
	else:
		# CHECK SESSION - SOFT VERSION - NO SAVE ON DB
		if not check_session(kanazzi, username, action='getRandomSong', store=False):
			response_data['result'] = 'failure'
			response_data['message'] = 'Invalid Session'
			return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
		
		# END CHECK SESSION

	song_rs = Song.objects.all()
	random_index = randint(0, len(song_rs) - 1)
	song = song_rs[random_index]

	if song:
		l = Lyric.objects.all().filter(id_song_id=song.id_song)
		k = []
		for rec in l:
			k.append({'id':rec.id_lyric, 'text':rec.lyric})
		out = {'title':song.title, 'author':song.author, 'lyrics':k}
		response_data['message'] = out
	else:
		response_data['message'] = 'song not found'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_songs(request):

	response_data = {}
	response_data['result'] = 'success'
	response_data['payload'] = serializers.serialize("json", Song.objects.all())

	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_lyrics_by_song(request):
	
	response_data = {}
	response_data['result'] = 'success'
	
	try:
		int(request.GET['id_song'])
	except:
		response_data['result'] = 'error'
		response_data['message'] = 'not valid id'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	s = Song.objects.filter(id_song=request.GET['id_song'])

	if s:
		s = s[0]
		l = Lyric.objects.all().filter(id_song_id=s.id_song)
		k = []
		for rec in l:
			k.append({'id':rec.id_lyric, 'text':rec.lyric})
		out = {'title':s.title, 'author':s.author, 'lyrics':k}
		response_data['message'] = json.dumps(out)
	else:
		response_data['message'] = 'song not found'
		return HttpResponse(json.dumps(response_data), content_type="application/json")


	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_movies(request):

	response_data = {}
	response_data['result'] = 'success'
	response_data['payload'] = serializers.serialize("json", Movie.objects.all())

	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_dogma(request):

	response_data = {}
	
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')
	
	if not username and not kanazzi:
		username = request.GET.get('username','')
		kanazzi = request.GET.get('kanazzi','')
		print("A client is using a deprecated GET method for get dogma")    
	'''
	# CHECK SESSION - SOFT VERSION - NO SAVE ON DB
	if not check_session(kanazzi, username, action='getDogma', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
	# END CHECK SESSION
	'''

	l = []
	rs = Minchiate.objects.filter(type='dogma')
	for rec in rs:
		l.append(rec.text)

	response_data['result'] = 'success'
	response_data['payload'] = l

	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_people(request):

	response_data = {}

	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')
	
	if not username and not kanazzi:
		username = request.GET.get('username','')
		kanazzi = request.GET.get('kanazzi','')
		print("A client is using a deprecated GET method for get people")
	'''
	# CHECK SESSION - SOFT VERSION - NO SAVE ON DB
	if not check_session(kanazzi, username, action='getDogma', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
	# END CHECK SESSION
	'''
		
	l = []
	rs = Minchiate.objects.filter(type='people')
	for rec in rs:
		d = json.loads(rec.text)
		l.append(d)

	response_data['result'] = 'success'
	response_data['payload'] = l

	return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_pesate_by_soggetto(request, id_soggetto):

	response_data = {}    
	s = Soggetto.objects.filter(id_soggetto=id_soggetto)
	
	if s:
		s=s[0]
		l = Pesata.objects.filter(id_soggetto=id_soggetto)
		peso_list = []
		for peso in l:
			d = {'data':peso.data.strftime("%d/%m/%y"), 'peso':peso.peso}
			d = utils.decimal_dumps(d)
			peso_list.append(d)
		response_data['message'] = {'nome': s.nome, 'cognome': s.cognome, 'pesate':peso_list}
	else:
		response_data['message'] = {}
	#peso_list = json.dumps(peso_list)
	
	response_data['result'] = 'success'
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_all_pesate(request):
	out = {}
	s = Soggetto.objects.values_list('id_soggetto','nome')
	for soggetto in s:
		l = Pesata.objects.filter(id_soggetto=soggetto)
		peso_list = []
		for peso in l:
			d = {'data':peso.data.strftime("%Y/%m/%d"), 'peso':peso.peso}
			d = utils.decimal_dumps(d)
			'''
			print("========================")
			print(d)
			print("========================")
			'''
			peso_list.append(d)
		
		#peso_list = peso_list.sort(key=operator.itemgetter('data'))
			
		#peso_list = json.dumps(peso_list)
		out[soggetto[0]] = {}
		out[soggetto[0]]['nome'] = soggetto[1]        
		out[soggetto[0]]['pesate'] = peso_list
	
	response_data = {}
	response_data['result'] = 'success'
	response_data['message'] = out
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_sum_by_month(request):
	out = {}
	s = Soggetto.objects.values_list('id_soggetto','nome')
	for soggetto in s:
		l = Pesata.objects.filter(id_soggetto=soggetto[0]) #.order_by('data')
		peso_list = []
		mesi_diz = {}
		for peso in l:
			mese_anno = peso.data.strftime("%Y%m")
			if mese_anno not in mesi_diz:
				mesi_diz[mese_anno] = {'pesi_mese':[]}
			mesi_diz[mese_anno]['pesi_mese'].append(peso.peso)
			mesi_diz[mese_anno]['last_data'] = peso.data.strftime("%Y/%m/%d")
		
		l = list(mesi_diz.keys())
		l.sort()
			
		for mese_anno in l:    
			cum_peso = mesi_diz[mese_anno]['pesi_mese'][0] - mesi_diz[mese_anno]['pesi_mese'][-1]
			d = {'data':mesi_diz[mese_anno]['last_data'], 'peso':cum_peso}
			d = utils.decimal_dumps(d)
			peso_list.append(d)
			
		#peso_list = json.dumps(peso_list)
		out[soggetto[0]] = {}
		out[soggetto[0]]['nome'] = soggetto[1]        
		out[soggetto[0]]['pesate'] = peso_list
	
	response_data = {}
	response_data['result'] = 'success'
	response_data['message'] = out
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def check_session(session_id, username, action='', store=False):
	print("Classic check session starting")
	SESSION_DBG=True
	session_id = session_id.strip()
	sessions = Session.objects.filter(session_string=session_id)
	if len(sessions) > 0:
		#print "session already exists"
		return False
	else:
		#Semantic check
		decryption_suite = AES.new(os.environ['OPENSHIFT_DUMMY_KEY'], AES.MODE_ECB, '')
		plain_text = decryption_suite.decrypt( base64.b64decode(session_id) )
		try:
			#print session_id.strip()
			plain_text = plain_text.strip()
			session_dt = datetime.strptime(str(plain_text.decode("utf-8")), "%Y_%m_%d_%H_%M_%S_%f")
			if SESSION_DBG: print("Valid session id for user %s" % username)
			now = datetime.now()
			td = now - session_dt
			
			if td.days > 90:
				if SESSION_DBG: print("Session expired : " + str(td.days) + " days")
				return False
			else:
				if SESSION_DBG: print("Session not expired : " + str(td.days) + " days")
				pass
			
		except Exception as ee:
			if SESSION_DBG: print(ee)
			if SESSION_DBG: print("Not valid session id")
			return False
		
		if store:
			s=Session(session_string=session_id, username=username, action=action)
			s.save()
			
		return True 


@ensure_csrf_cookie
def saveminchiata(request):

	response_data = {}
	response_data['result'] = 'success'

	type = request.POST.get('type','')
	dogma = request.POST.get('dogma','')
	name = request.POST.get('name','')
	desc = request.POST.get('desc','')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')

	if not check_session(kanazzi, username, action='saveminchiata', store=True):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

	if type and type == 'people' and name and desc:
		d = {'name':name, 'desc':desc}
		m = Minchiate(type=type, text=json.dumps(d))
		m.save()
	elif type and type == 'dogma' and dogma:
		m = Minchiate(type=type, text=dogma)
		m.save()
	else:
		response_data['result'] = 'failure'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)
		
	return HttpResponse(json.dumps(response_data), content_type="application/json")


def login(request):
	
	response_data = {}
	response_data['result'] = 'success'
	try:
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		print(list(request.POST.keys()))
		print(username)
		
		if username=='':
			response_data['result'] = 'failure'
			response_data['payload'] = {"message": "Not valid credentials", 'logged':'no'}
			return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
		
		decryption_suite = AES.new(os.environ['OPENSHIFT_DUMMY_KEY'], AES.MODE_ECB, '')
		plain_text = decryption_suite.decrypt( base64.b64decode(password) )
		 
		out = ""
		logged = "no"
		u = User.objects.filter(username=username)
		
		if len(u) > 0:
			plain_text = plain_text.decode('utf-8').strip()
			pwd_ok = check_password(plain_text, u[0].password)
			out = "User found!"
			if pwd_ok:
				logged = "yes"
		else:
			out = "User not found!"
			logged = "no"
		
		print("login result for user " + username + " : " + out)
		
		response_data['payload'] = {"message":out, 'username':username, 'logged':logged}
	except Exception as eee:
		response_data['result'] = 'failure'
		response_data['payload'] = {}
		print(eee)

	if logged == "no":
		response_data['payload'] = {"message": "Not valid credentials", 'logged':'no'}
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
		
	return HttpResponse(json.dumps(response_data), content_type="application/json")


def geolocation(request):
	
	response = {'result':'success'}
	username = request.POST.get('username', '')
	longitude = request.POST.get('longitude', '')
	latitude = request.POST.get('latitude', '')
	photo = request.POST.get('photo','')
	action = request.POST.get('action', '')
	kanazzi = request.POST.get('kanazzi','').strip()

	if not username or not kanazzi or not check_session(kanazzi, username, action='geolocation', store=True):
		response['result'] = 'failure'
		response['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response), content_type="application/json", status=401)

	if not action or action not in ('GET','SET','DELETE'):
		response = {'result':'failure'}
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)

	u = User.objects.filter(username=username)
	loc = Location.objects.filter(user=u[0])
	
	if action == 'DELETE':
		#DELETE
		print("DELETE")
		if loc:
			loc[0].delete()
			response['message'] = 'GPS coordinates have been delete from the system for user %s' % username
		else:
			response['message'] = 'GPS coordinates not available for user %s, deletion not needed.' % username
		return HttpResponse(json.dumps(response), content_type="application/json", status=200)

	elif action == 'GET':
		locations = Location.objects.all()
		out = []
		for location in locations:
			d = {
				'name':location.user.username,
				'latitude':str(location.latitude),
				'longitude':str(location.longitude),
				'photo':location.photo,
				'last_locate':str(location.updated)
				}
			out.append(d)
		response['body'] = out
		response['message'] = 'Retrieved GPS coordinates for %s user(s)' % len(locations)
		return HttpResponse(json.dumps(response), content_type="application/json", status=200)

	elif action == 'SET':
		if latitude and longitude:            #SET COORD
			if loc:
				loc[0].latitude = latitude
				loc[0].longitude = longitude
				if photo: loc[0].photo = photo
				loc[0].save()
			else:
				l = Location(user=u[0], latitude=latitude, longitude=longitude, photo=photo)
				l.save()
			response['message'] = 'GPS coordinates have been created/updated for user %s' % username
			return HttpResponse(json.dumps(response), content_type="application/json", status=200)
		else:
			return HttpResponse(json.dumps(response), content_type="application/json", status=400)
	else:
		response['result'] = 'failure'
		return HttpResponse(json.dumps(response), content_type="application/json", status=405)


def geolocation2(request):
	
	response = {'result':'success'}
	
	try:
		i_data = json.loads(request.body)
		print("Valid JSON data received.")
		print(i_data)
		username = i_data.get('username', '')
		action = i_data.get('action', '')
		longitude = i_data.get('longitude', '')
		latitude = i_data.get('latitude', '')
		photo = i_data.get('photo','')
		firebase_id_token = i_data.get('firebase_id_token', '')
		kanazzi = i_data.get('kanazzi', '')
	except:
		response['result'] = 'failure'
		response['message'] = 'Bad input format'
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)

	print("Checking firebase id token.... Result: " + str(checkFBTokenLocal(firebase_id_token)))

	if not username or ( not checkFBTokenLocal(firebase_id_token) and not check_session(kanazzi, username, action='geolocation2', store=True) ):
		response['result'] = 'failure'
		response['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response), content_type="application/json", status=401)

	if not action or action not in ('GET','SET','DELETE'):
		response = {'result':'failure'}
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)

	u = User.objects.filter(username=username)
	loc = Location.objects.filter(user=u[0])
	
	if action == 'DELETE':
		#DELETE
		print("DELETE")
		if loc:
			loc[0].delete()
			response['message'] = 'GPS coordinates have been delete from the system for user %s' % username
		else:
			response['message'] = 'GPS coordinates not available for user %s, deletion not needed.' % username
		return HttpResponse(json.dumps(response), content_type="application/json", status=200)

	elif action == 'GET':
		locations = Location.objects.all()
		out = []
		for location in locations:
			d = {
				'name':location.user.username,
				'latitude':str(location.latitude),
				'longitude':str(location.longitude),
				'photo':location.photo,
				'last_locate':str(location.updated)
				}
			out.append(d)
		response['body'] = out
		response['message'] = 'Retrieved GPS coordinates for %s user(s)' % len(locations)
		return HttpResponse(json.dumps(response), content_type="application/json", status=200)

	elif action == 'SET':
		if latitude and longitude:            #SET COORD
			if loc:
				loc[0].latitude = latitude
				loc[0].longitude = longitude
				loc[0].save()
			else:
				l = Location(user=u[0], latitude=latitude, longitude=longitude)
				l.save()
			response['message'] = 'GPS coordinates have been created/updated for user %s' % username
			return HttpResponse(json.dumps(response), content_type="application/json", status=200)
		else:
			return HttpResponse(json.dumps(response), content_type="application/json", status=400)
	else:
		response['result'] = 'failure'
		return HttpResponse(json.dumps(response), content_type="application/json", status=405)

def setFBToken(request):
	
	response = {'result':'success'}
	
	print(" ====== request info =====")
	print(request.method)
	print(request.content_type)
	print(" =========================")
	
	try:
		i_data = json.loads(request.body)
		print("Valid data received.")
		print(i_data)
		username = i_data.get('username', '')
		token = i_data.get('token', '')
		idToken = i_data.get('id_token', '')
		appVersion = i_data.get('app_version', '')
	except:
		response['result'] = 'failure'
		response['message'] = 'Bad input format'
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)

	if username:
		users = User.objects.filter(username=username)
		if users:
			u=users[0]
			
			'''
			auth_result = check_session_firebase('',u.username)
			print auth_result
			'''
			u.app_version = appVersion
			if token: u.fcm_token = token
			if idToken: u.firebase_id_token = idToken
			u.save()
			return HttpResponse(json.dumps(response), content_type="application/json", status=200)
		else:
			response['result'] = 'failure'
			return HttpResponse(json.dumps(response), content_type="application/json", status=401)
	else:
		response['result'] = 'failure'
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)

def checkFBToken(request):
	
	SESSION_DBG=True
	response = {"result":"success", "message":""}
	
	try:
		i_data = json.loads(request.body)
		username = i_data.get('username', '')
		if SESSION_DBG: print('Starting session check for user %s' % username)
	
	
		#Google Initializazion
		google_account_file = os.environ.get('GOOGLE_JSON','')
		if not google_account_file:
			raise ValueError('Google JSON account file not found.')
			
		if (not len(firebase_admin._apps)):
			cred = credentials.Certificate(google_account_file)
			default_app = firebase_admin.initialize_app(cred)
		
		#Retrieving id_token from DB
		users = User.objects.filter(username=username)
		if not users:
			raise ValueError('User not found.')
		u = users[0]
		id_token = u.firebase_id_token
		if not id_token:
			raise ValueError('idToken is empty!')
			
		#Verifying id token
		decoded_token = auth.verify_id_token(id_token)
	
		response["message"] = "Firebase idToken successulfy verified"
		response["payload"] = {"firebase_id_token":id_token}
	
	except Exception as ee:
		print(ee)
		if 'Token expired' in ee:
			response = {"result":"failure", "message":"token expired"}
			return HttpResponse(json.dumps(response), content_type="application/json", status=401)
		else:
			response = {"result":"failure", "message":str(ee)}
			return HttpResponse(json.dumps(response), content_type="application/json", status=500)


	return HttpResponse(json.dumps(response), content_type="application/json", status=200)


def checkFBTokenLocal(id_token):
	
	SESSION_DBG=True
	response = False
	
	try:
		if SESSION_DBG: print('Starting firebase id token check...')
	
		#Google Initializazion
		google_account_file = os.environ.get('GOOGLE_JSON','')
		if not google_account_file:
			raise ValueError('Google JSON account file not found.')
			
		if (not len(firebase_admin._apps)):
			cred = credentials.Certificate(google_account_file)
			default_app = firebase_admin.initialize_app(cred)

		#Verifying id token
		decoded_token = auth.verify_id_token(id_token)
	
		response = True
	
	except Exception as ee:

		if 'Token expired' in ee:
			if SESSION_DBG: print('Token expired!')
		else:
			if SESSION_DBG: print(str(ee))

	return response

def check_google(token):
	try:
		# Specify the CLIENT_ID of the app that accesses the backend:
		idinfo = id_token.verify_oauth2_token(token, google_requests.Request())

		# Or, if multiple clients access the backend server:
		# idinfo = id_token.verify_oauth2_token(token, requests.Request())
		# if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
		#     raise ValueError('Could not verify audience.')

		if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
			raise ValueError('Wrong issuer.')

		# If auth request is from a G Suite domain:
		# if idinfo['hd'] != GSUITE_DOMAIN_NAME:
		#     raise ValueError('Wrong hosted domain.')

		# ID token is valid. Get the user's Google Account ID from the decoded token.
		userid = idinfo['sub']
		return True
		
	except ValueError as ee:
		# Invalid token
		print(str(ee))
		return False

def test_session(request):
	
	response = {'result':'success'}
	
	try:
		i_data = json.loads(request.body)
		print("Valid JSON data received.")
		username = i_data.get('username', '')
		firebase_id_token = i_data.get('firebase_id_token', '')
		kanazzi = i_data.get('kanazzi', '')
	except:
		response['result'] = 'failure'
		response['message'] = 'Bad input format'
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)

	token_check = check_google(firebase_id_token)
	user_check = check_session(kanazzi, username, action='geolocation2', store=True)

	if not username or ( not token_check and not user_check ):
		response['result'] = 'failure'
		response['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response), content_type="application/json", status=401)
		
	response['message'] = 'Authentication successful! By User:%s - by Token: %s' % (user_check, token_check)
	return HttpResponse(json.dumps(response), content_type="application/json", status=200)

