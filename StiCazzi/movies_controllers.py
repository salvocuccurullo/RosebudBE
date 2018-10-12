import json, decimal, datetime, operator, base64, os, time, hashlib
from random import randint
from datetime import date, datetime
from django.core import serializers
from Crypto.Cipher import AES

from django.http import HttpResponse
from StiCazzi.models import Movie, TvShow, User, TvShowVote, Session, Notification, Catalogue
from StiCazzi.controllers import check_session
from StiCazzi.covers_controllers import upload_cover
from StiCazzi.utils  import decimal_dumps, safe_file_name

from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.hashers import *
from django.forms.models import model_to_dict
from django.db.models import Q, F, Count


def get_tvshows_new(request):

	response = {'result':'success'}
	
	try:
		i_data = json.loads(request.body)
		print("Valid JSON data received.")
		print(i_data)
		username = i_data.get('username', '')
		firebase_id_token = i_data.get('firebase_id_token', '')
		kanazzi = i_data.get('kanazzi', '')
		query = i_data.get('query', '')
		limit = i_data.get('limit', 15)
		current_page = i_data.get('current_page', 1)
	except:
		response['result'] = 'failure'
		response['message'] = 'Bad input format'
		return HttpResponse(json.dumps(response), content_type="application/json", status=400)
	
	if not username or not kanazzi or not check_session(kanazzi, username, action='gettvshows2', store=True):
		response['result'] = 'failure'
		response['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response), content_type="application/json", status=401)
	
	if query and len(query) < 4:
		response['result'] = 'failure'
		response['message'] = 'Query String too short'
		return HttpResponse(json.dumps(response), content_type="application/json", status=404)

	out_list = []
	charts = {}
	l = TvShow.objects.filter(
			Q(title__icontains=query) | Q(media__icontains=query)
		).order_by('-datetime')

	lower_bound = limit * (current_page - 1) 
	upper_bound = current_page * limit
	bounded = l[lower_bound:upper_bound]

	for tvs in l[lower_bound:upper_bound]:
		#dt = tvs.datetime.strftime("%A, %d. %B %Y %I:%M%p")
		dt = tvs.datetime.strftime("%d %B %Y ")
		dtsec = time.mktime(tvs.datetime.timetuple())
		tvsv = TvShowVote.objects.filter(tvshow=tvs)
		avgVote = 0
		valid_vote_count=0
		u_v_dict = {}

		for voteX in tvsv:
			if not voteX.now_watching:
				avgVote += voteX.vote
				valid_vote_count += 1
			us_dt = voteX.created.strftime("%A, %d. %B %Y %I:%M%p")
			str_vote = str(decimal.Decimal(voteX.vote))
			u_v_dict[voteX.user.username] = {'us_username':voteX.user.username, 'us_name':voteX.user.name, 'us_vote':str_vote, 'us_date':us_dt}
			u_v_dict[voteX.user.username].update({'now_watching':voteX.now_watching, 'episode':voteX.episode, 'season':voteX.season, 'comment':voteX.comment})
			
		if tvsv and avgVote:
			avgVote = float(avgVote) / float(valid_vote_count)
		else:
			avgVote = 0
		str_vote1 = str(decimal.Decimal(tvs.vote))
		avgVote_str = "%.2f" % avgVote
		d = {'title':tvs.title, 'media':tvs.media, 'vote':str_vote1, 'username':tvs.user.username, 'name':tvs.user.name, 'poster':tvs.poster}
		d.update( {'datetime_sec':dtsec, 'u_v_dict':u_v_dict} )
		d.update( {'type': tvs.type, 'tvshow_type': tvs.tvshow_type, 'director':tvs.director, 'year':tvs.year, 'id':tvs.id_tv_show, 'link':tvs.link, 'datetime':dt, 'avg_vote':avgVote_str} )
		out_list.append(d)

	has_more = True
	if len(l) <= upper_bound:
		has_more = False
		
	votes_user = TvShowVote.objects.annotate(name=F('user__username')).values("name").annotate(count=Count('user'))
	votes_user = [{"name":rec['name'], "count":rec['count']} for rec in list(votes_user)]

	response['payload'] = {'tvshows': out_list, 'query': query, 'has_more':has_more, 'votes_user': votes_user}

	return HttpResponse(json.dumps(response), content_type="application/json")

def get_movies_ct(request):

	l = Movie.objects.all().exclude(cinema="")
	out = []
	for rec in l:
		d = {'id': rec.id_movie, 'title':rec.title, 'year':rec.year, 'cinema':rec.cinema, 'cast':rec.cast, 'director':rec.director, 'filmtv':rec.filmtv}
		out.append(d)
		
	response_data = {}
	response_data['result'] = 'success'
	response_data['payload'] =  out

	return HttpResponse(json.dumps(response_data), content_type="application/json")

@ensure_csrf_cookie
def deletemovie(request):

	response_data = {}
	response_data['result'] = 'success'
	id = request.POST.get('id','')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')

	if not kanazzi or not username or not check_session(kanazzi, username, action='deletemovie', store=True):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
	
	u=User.objects.filter(username=username)
	#Check existing votes
	tvrs = TvShowVote.objects.filter(tvshow=id).exclude(user=u[0])
	if len(tvrs) > 0:
		delShow = tvrs[0]
		response_data['message'] = 'Cannot delete %s. It has been voted by some kaeroeso !' % (delShow.tvshow.title)
		response_data['result'] = 'failure'
	else:        
		t = TvShow.objects.filter(id_tv_show=id)
		if len(t)>0:
			tvshow = t[0]
			tvshow.delete()
			response_data['message'] = 'Tvshow with id=' + id + " deleted succcessfully."
		else:
			response_data['result'] = 'failure'
			response_data['message'] = 'Cannot delete tvshow with id=' + id + ". It does not exist!"
		
	return HttpResponse(json.dumps(response_data), content_type="application/json")


def create_update_vote(u, tvshow, dv):
	tvsv = TvShowVote.objects.filter(user=u, tvshow=tvshow[0])
	if len(tvsv) == 0:
		tvsv = TvShowVote(vote=dv['vote'], user=u, tvshow=tvshow[0], now_watching=dv["nw"], season=dv["season"], episode=dv["episode"], comment=dv['comment'])        
		tvsv.save()

		if not dv["nw"]:
			n = Notification(type="new_vote", title="%s has just voted for a movie..."  % u.username, message="Title: %s - Vote: %s " % (tvshow[0].title, dv["vote"]), username=u.username)
			n.save()
	else:
		tx = tvsv[0]
		if dv['giveup']:
			tx.delete()
			
			n = Notification(type="give_up", title="%s has just gave up to follow a movie" % u.username, message="%s" % tvshow[0].title, username=u.username)
			n.save()
			
		else:
			
			finished = False
			first_comment = False
			
			if tx.now_watching and not dv["nw"]:
				finished = True
			
			if tx.comment == "" and dv["comment"] != "":
				first_comment = True
			
			tx.vote = dv['vote']
			tx.now_watching = dv["nw"]
			tx.episode = dv["episode"]
			tx.season = dv["season"]
			tx.comment = dv["comment"]
			tx.save()
			
			if finished:
				n = Notification(type="new_vote", title="%s has just voted for a movie..."  % u.username, message="Title: %s - Vote: %s " % (tvshow[0].title, dv["vote"]), username=u.username)
				n.save()
				
			if first_comment:
				n = Notification(type="new_comment", title="%s has just set a comment for a movie..."  % u.username, message="Title: %s - %s... " % (tvshow[0].title, dv["comment"][:30]), username=u.username)
				n.save()
	
	print(dv)
	if dv["nw"] and str(dv["season"]) == "1" and str(dv["episode"]) == "1":
		n = Notification(type="new_nw", title="%s has just started to watch a movie..."  % u.username, message="Title: %s - S%s E%s " % (tvshow[0].title, dv["season"], dv["episode"]), username=u.username)
		n.save()


@ensure_csrf_cookie
def savemovie(request):

	response_data = {}
	response_data['result'] = 'success'

	id = request.POST.get('id','')
	title = request.POST.get('title','')
	media = request.POST.get('media','')
	link = request.POST.get('link','')
	vote = request.POST.get('vote','')
	type = request.POST.get('type','')
	director = request.POST.get('director','')
	year = request.POST.get('year','')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')
	nw = request.POST.get('nw', False)
	
	if nw == "true":
		nw = True
	else:
		nw = False
	
	if not check_session(kanazzi, username, action='savemovie', store=True):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
	
	t = TvShow.objects.filter(id_tv_show=id)
	u = User.objects.filter(username=username)[0]
	
	if len(t)>0 and username != t[0].user.username:
		print("User not owner of the movie is voting...")
		data_vote = {'nw': nw, 'episode': 1, 'season':1, 'vote':vote, 'giveup':False}
		create_update_vote(u, t, data_vote)
 
	else:
		if len(t) == 0:
			
			#Check duplicate title
			tvrs = TvShow.objects.filter(title=title)
			if len(tvrs) > 0:
				dupShow = tvrs[0]
				response_data['message'] = 'TvShow/Movie %s already exists. Created by %s!' % (dupShow.title, dupShow.user.name)
				response_data['result'] = 'failure'
			else:    
				print("Adding tvshow... Title: " + title)
				tvshow = TvShow(title=title, media=media, link=link, vote=vote, user=u, type=type, director=director, year=year)
				tvshow.save()
				
				tvsv = TvShowVote(vote=vote, user=u, tvshow=tvshow, now_watching=nw)
				tvsv.save()
	
				response_data['message'] = 'TvShow/Movie %s saved!' % title            
		else:
			print("Updating tvshow... Title: " + title)
			tvshow = t[0]
			tvshow.title=title 
			tvshow.media=media 
			tvshow.link=link
			tvshow.vote=vote
			tvshow.type=type
			tvshow.director=director
			tvshow.year=year
			tvshow.save()
			
			data_vote = {'nw': nw, 'episode': episode, 'season':season, 'vote':vote, 'giveup':False}
			create_update_vote(u, t, data_vote)
		
	return HttpResponse(json.dumps(response_data), content_type="application/json")

@ensure_csrf_cookie
def savemovienew(request):

	response_data = {}
	response_data['result'] = 'success'

	id = request.POST.get('id','')
	title = request.POST.get('title','')
	media = request.POST.get('media','')
	link = request.POST.get('link','')
	vote = request.POST.get('vote','')
	type = request.POST.get('type','brand_new')
	tvshow_type = request.POST.get('tvshow_type','movie')
	director = request.POST.get('director','')
	year = request.POST.get('year','')
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')
	nw = request.POST.get('nw', False)
	giveup = request.POST.get('giveup', False)
	later = request.POST.get('later', False)
	season = request.POST.get('season', 1)
	episode = request.POST.get('episode', 1)
	comment = request.POST.get('comment', '')
	f = request.FILES.get('pic','')
	poster_name = ''
	upload_file_res = {} 
	
	print(id)
	'''
	print "================"
	print id
	print title
	print media
	print type
	print "================"
	'''
	
	if f:
		print("A file has been uploaded... " + f.name)
		temp_f_name = title + '_' + f.name
		poster_name = safe_file_name(temp_f_name, f.content_type)
		
	if nw == "on":
		nw = True
	else:
		nw = False

	if giveup == "on":
		giveup = True
	else:
		giveup = False

	if later == "on":
		later = True
	else:
		later = False
 
	if not season : season = 1
	if not episode : episode = 1
 
	if not check_session(kanazzi, username, action='savemovienew', store=True):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

	if not title or not media or not type:
		response_data['result'] = 'failure'
		response_data['message'] = 'Missing required data: check title, media and type'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	t = TvShow.objects.filter(id_tv_show=id)
	u = User.objects.filter(username=username)[0]
	
	if len(t)>0 and username != t[0].user.username:
		print("User not owner of the movie is voting...")
		data_vote = {'nw': nw, 'episode': episode, 'season':season, 'vote':vote, 'giveup':giveup, 'comment':comment}
	   
		tvshow = t[0]
 
		if not later:
			create_update_vote(u, t, data_vote)
		
		'''
			New feature: to allow not movie owner to upload the poster and set a link
		'''

		if f:
			upload_file_res = upload_cover(request, poster_name)
							
		upload_res = upload_file_res.get('result','failure')
		if upload_res == 'failure':
			poster_name = ''
		else:
			tvshow.poster=poster_name

		if link:
			tvshow.link = link

		if upload_res != 'failure' or (tvshow.link == "" and link):
			tvshow.save()

			n = Notification(type="new_movie", title="%s has just added a new movie poster or a link" %username, message="Title: %s" % title, username=username)
			n.save()

		'''
			End New feature
		'''
 
	else:
		if len(t) == 0:
			
			#Check duplicate title
			tvrs = TvShow.objects.filter(title=title)
			if len(tvrs) > 0:
				dupShow = tvrs[0]
				response_data['message'] = 'TvShow/Movie %s already exists. Created by %s!' % (dupShow.title, dupShow.user.name)
				response_data['result'] = 'failure'
			else:

				if f:
					upload_file_res = upload_cover(request, poster_name)
									
				upload_res = upload_file_res.get('result','failure')
				if upload_res == 'failure':
					poster_name = ''
				
				print("Adding tvshow... Title: " + title)
			
				tvshow = TvShow(title=title, media=media, link=link, vote=vote, user=u, type=type, tvshow_type=tvshow_type, director=director, year=year, poster=poster_name)
				tvshow.save()
				
				if not later:
					tvsv = TvShowVote(vote=vote, user=u, tvshow=tvshow, now_watching=nw, season=season, episode=episode, comment=comment)
					tvsv.save()

				n = Notification(type="new_movie", title="%s has just added a new movie" %username, message="Title: %s" % title, username=username)
				n.save()

				response_data['message'] = 'TvShow/Movie %s saved!' % title

		else:

			if f:
				upload_file_res = upload_cover(request, poster_name)
				
			upload_res = upload_file_res.get('result','failure')
			if upload_res == 'failure':
				poster_name = ''
			else:
				n = Notification(type="new_movie", title="%s has just added a new movie poster" %username, message="Title: %s" % title, username=username)
				n.save()
			
			print("Updating tvshow... Title: " + title)
			tvshow = t[0]
			tvshow.title=title 
			tvshow.media=media 
			tvshow.link=link
			tvshow.vote=vote
			tvshow.type=type
			tvshow.tvshow_type=tvshow_type
			tvshow.director=director
			tvshow.year=year
			if poster_name:
				tvshow.poster=poster_name
			tvshow.save()
			
			data_vote = {'nw': nw, 'episode': episode, 'season':season, 'vote':vote, 'giveup':giveup, 'comment':comment}
			if not later:
				create_update_vote(u, t, data_vote)
				
	response_data.update( {"upload_result":upload_file_res} )
				
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_tvshows(request):

	response_data = {}
	username = request.POST.get('username','')
	kanazzi = request.POST.get('kanazzi','')
	
	if not username and not kanazzi:
		username = request.GET.get('username','')
		kanazzi = request.GET.get('kanazzi','')
		print("A client is using a deprecated GET method for get tv shows")
				
	if not username or not kanazzi or not check_session(kanazzi, username, action='gettvshows', store=False):
		response_data['result'] = 'failure'
		response_data['message'] = 'Invalid Session'
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

	response_data['result'] = 'success'
	out_list = []
	charts = {}
	l = TvShow.objects.filter().order_by('-datetime')
	for tvs in l:
		#dt = tvs.datetime.strftime("%A, %d. %B %Y %I:%M%p")
		dt = tvs.datetime.strftime("%d %B %Y ")
		dtsec = time.mktime(tvs.datetime.timetuple())
		tvsv = TvShowVote.objects.filter(tvshow=tvs)
		avgVote = 0
		valid_vote_count=0
		u_v_dict = {}

		for voteX in tvsv:            
			if not voteX.now_watching:
				avgVote += voteX.vote
				valid_vote_count += 1
			us_dt = voteX.created.strftime("%A, %d. %B %Y %I:%M%p")
			str_vote = str(decimal.Decimal(voteX.vote))
			u_v_dict[voteX.user.username] = {'us_username':voteX.user.username, 'us_name':voteX.user.name, 'us_vote':str_vote, 'us_date':us_dt}
			u_v_dict[voteX.user.username].update({'now_watching':voteX.now_watching, 'episode':voteX.episode, 'season':voteX.season, 'comment':voteX.comment})
			
		if tvsv and avgVote:
			avgVote = float(avgVote) / float(valid_vote_count)
		else:
			avgVote = 0
		str_vote1 = str(decimal.Decimal(tvs.vote))
		avgVote_str = "%.2f" % avgVote
		d = {'title':tvs.title, 'media':tvs.media, 'vote':str_vote1, 'username':tvs.user.username, 'name':tvs.user.name, 'poster':tvs.poster}
		d.update( {'datetime_sec':dtsec, 'u_v_dict':u_v_dict} )
		d.update( {'type': tvs.type, 'director':tvs.director, 'year':tvs.year, 'id':tvs.id_tv_show, 'link':tvs.link, 'datetime':dt, 'avg_vote':avgVote_str} )
		out_list.append(d)
	
	voteUser = {}
	vote_user = []
	allVotes = TvShowVote.objects.all()
	for votex in allVotes:
		if votex.user.username in voteUser:
			voteUser[votex.user.username] += 1
		else:
			voteUser[votex.user.username] = 1
	for k in voteUser:
		vote_user.append({'name':k, 'count':voteUser[k]})
	
	payload = {'tvshows' : out_list, 'votes_user':vote_user}
	
	response_data['payload'] = json.dumps(payload)
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_movies_datatable(request):

	l = Movie.objects.all().exclude(cinema="")
	out = []
	for rec in l:
		d = {'0':rec.title, '1':rec.year, '2':rec.cinema, '3':rec.cast, '4':rec.director, '5':rec.filmtv}
		out.append(d)
		
	response_data = {}
	response_data['result'] = 'success'
	response_data['data'] =  out

	return HttpResponse(json.dumps(response_data), content_type="application/json")

