"""
 Django2 Movies Controller
"""

import json
import decimal
import time
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q, F, Count, Avg, CharField
from django.db.models.functions import Cast
from django.forms.models import model_to_dict

from StiCazzi.models import Movie, TvShow, User, TvShowVote, Notification, Catalogue
from StiCazzi.controllers import check_session
from StiCazzi.covers_controllers import upload_cover
from StiCazzi.utils import safe_file_name
logger = logging.getLogger(__name__)

def get_tvshows_new_opt(request):
    """ Get Tvshow New """
    logger.debug("Get Tvshows news opt called")
    response = {'result': 'success'}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        firebase_id_token = i_data.get('firebase_id_token', '')
        kanazzi = i_data.get('kanazzi', '')
        query = i_data.get('query', '')
        limit = i_data.get('limit', 15)
        current_page = i_data.get('current_page', 1)
        lazy_load = i_data.get('lazy_load', True)
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    if not check_session(kanazzi, username, action='gettvshows2', store=True):
        response['result'] = 'failure'
        response['message'] = 'Invalid Session'
        return JsonResponse(response, status=401)

    if query and len(query) < 4:
        response['result'] = 'failure'
        response['message'] = 'Query String too short'
        return JsonResponse(response, status=404)

    out_list = []
    movie_list = TvShow.objects.filter(
        Q(title__icontains=query) | Q(media__icontains=query)
    ).order_by('-created')

    lower_bound = limit * (current_page - 1)
    upper_bound = current_page * limit

    print("Lazy loading: " + str(lazy_load))
    if lazy_load:
        bounded = movie_list[lower_bound: upper_bound]
    else:
        bounded = movie_list

    for tvs in bounded:
        # dt = tvs.created.strftime("%A, %d. %B %Y %I:%M%p")
        movie_created = tvs.created.strftime("%d %B %Y ")
        dtsec = time.mktime(tvs.created.timetuple())

        tvshow_votes = TvShowVote.objects.filter(tvshow=tvs)
        avg_vote = tvshow_votes.filter(now_watching=0).aggregate(avg_vote=Avg("vote"))['avg_vote']
        if avg_vote:
            avg_vote_str = "%.2f" % avg_vote
        else:
            avg_vote_str = "0.0"

        dragon = tvshow_votes.values('episode', 'season', 'comment', 'now_watching')\
                             .annotate(us_username=F('user__username'))\
                             .annotate(us_name=F('user__name'))\
                             .annotate(us_vote=Cast('vote', CharField()))\
                             .annotate(us_date=Cast('created', CharField()))

        u_v_dict = {}
        for rec in list(dragon):
            u_v_dict[rec['us_username']] = rec

        tvshow_dict = {'title': tvs.title,
                       'media': tvs.media,
                       # 'vote': str_vote1,
                       'username': tvs.user.username,
                       'name': tvs.user.name,
                       'poster': tvs.poster,
                       'datetime_sec': dtsec,
                       'u_v_dict': u_v_dict,
                       'type': tvs.type,
                       'tvshow_type': tvs.tvshow_type,
                       'director': tvs.director,
                       'year': tvs.year,
                       'id': tvs.id_tv_show,
                       'link': tvs.link,
                       'datetime': movie_created,
                       'avg_vote': avg_vote_str,
                       'serie_season': tvs.serie_season
                      }
        out_list.append(tvshow_dict)

    has_more = True
    if len(movie_list) <= upper_bound:
        has_more = False
    if not lazy_load:
        has_more = False

    print("List size: " + str(len(bounded)))
    print("Has more: " + str(has_more))
    print("Query: " + query)
    print("Lower bound: " + str(lower_bound))
    print("Upper bound: " + str(upper_bound))

    tvshow_stat = TvShow.objects\
                  .filter(
                      Q(title__icontains=query) | Q(media__icontains=query)
                  )\
                  .values("tvshow_type")\
                  .annotate(count=Count('tvshow_type'))\
                  .values_list("tvshow_type", "count")

    votes_user = TvShowVote.objects.annotate(name=F('user__username'))\
                 .values("name")\
                 .annotate(count=Count('user'))\
                 .order_by('-count')
    votes_user = [{"name": rec['name'], "count": rec['count']} for rec in list(votes_user)]

    response['payload'] = {'stat': dict(tvshow_stat),
                           'tvshows': out_list,
                           'query': query,
                           'has_more': has_more,
                           'votes_user': votes_user,
                           'total_show': movie_list.count()
                          }

    return JsonResponse(response)


def get_tvshows_new(request):
    """ Get Tvshow New """

    response = {'result': 'success'}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        firebase_id_token = i_data.get('firebase_id_token', '')
        kanazzi = i_data.get('kanazzi', '')
        query = i_data.get('query', '')
        limit = i_data.get('limit', 15)
        current_page = i_data.get('current_page', 1)
        lazy_load = i_data.get('lazy_load', True)
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    if not check_session(kanazzi, username, action='gettvshows2', store=True):
        response['result'] = 'failure'
        response['message'] = 'Invalid Session'
        return JsonResponse(response, status=401)

    if query and len(query) < 4:
        response['result'] = 'failure'
        response['message'] = 'Query String too short'
        return JsonResponse(response, status=404)

    out_list = []
    movie_list = TvShow.objects.filter(
        Q(title__icontains=query) | Q(media__icontains=query)
    ).order_by('-created')

    lower_bound = limit * (current_page - 1)
    upper_bound = current_page * limit

    print("Lazy loading: " + str(lazy_load))
    if lazy_load:
        bounded = movie_list[lower_bound: upper_bound]
    else:
        bounded = movie_list

    for tvs in bounded:
        # dt = tvs.created.strftime("%A, %d. %B %Y %I:%M%p")
        movie_created = tvs.created.strftime("%d %B %Y ")
        dtsec = time.mktime(tvs.created.timetuple())
        tvshow_votes = TvShowVote.objects.filter(tvshow=tvs)
        avg_vote = 0
        valid_vote_count = 0
        u_v_dict = {}

        for tvshow_vote in tvshow_votes:
            if not tvshow_vote.now_watching:
                avg_vote += tvshow_vote.vote
                valid_vote_count += 1
            us_dt = tvshow_vote.created.strftime("%A, %d. %B %Y %I:%M%p")
            str_vote = str(decimal.Decimal(tvshow_vote.vote))
            u_v_dict[tvshow_vote.user.username] = {'us_username': tvshow_vote.user.username,
                                                   'us_name': tvshow_vote.user.name,
                                                   'us_vote': str_vote,
                                                   'us_date': us_dt,
                                                   'now_watching': tvshow_vote.now_watching,
                                                   'episode': tvshow_vote.episode,
                                                   'season': tvshow_vote.season,
                                                   'comment': tvshow_vote.comment
                                                  }

        if tvshow_votes and avg_vote:
            avg_vote = float(avg_vote) / float(valid_vote_count)
        else:
            avg_vote = 0
        str_vote1 = str(decimal.Decimal(tvs.vote))
        avg_vote_str = "%.2f" % avg_vote
        tvshow_dict = {'title': tvs.title,
                       'media': tvs.media,
                       'vote': str_vote1,
                       'username': tvs.user.username,
                       'name': tvs.user.name,
                       'poster': tvs.poster,
                       'datetime_sec': dtsec,
                       'u_v_dict': u_v_dict,
                       'type': tvs.type,
                       'tvshow_type': tvs.tvshow_type,
                       'director': tvs.director,
                       'year': tvs.year,
                       'id': tvs.id_tv_show,
                       'link': tvs.link,
                       'datetime': movie_created,
                       'avg_vote': avg_vote_str,
                       'serie_season': tvs.serie_season
                      }
        out_list.append(tvshow_dict)

    has_more = True
    if len(movie_list) <= upper_bound:
        has_more = False
    if not lazy_load:
        has_more = False

    print("List size: " + str(len(bounded)))
    print("Has more: " + str(has_more))
    print("Query: " + query)
    print("Lower bound: " + str(lower_bound))
    print("Upper bound: " + str(upper_bound))

    tvshow_stat = TvShow.objects\
                  .filter(
                      Q(title__icontains=query) | Q(media__icontains=query)
                  )\
                  .values("tvshow_type")\
                  .annotate(count=Count('tvshow_type'))\
                  .values_list("tvshow_type", "count")

    votes_user = TvShowVote.objects.annotate(name=F('user__username'))\
                 .values("name")\
                 .annotate(count=Count('user'))\
                 .order_by('-count')
    votes_user = [{"name": rec['name'], "count": rec['count']} for rec in list(votes_user)]

    response['payload'] = {'stat': dict(tvshow_stat),
                           'tvshows': out_list,
                           'query': query,
                           'has_more': has_more,
                           'votes_user': votes_user,
                           'total_show': movie_list.count()
                          }

    return JsonResponse(response)


def get_movies_ct(request):
    """ Get Tvshow CT """

    movie_list = Movie.objects.all().exclude(cinema="")
    out = []
    for rec in movie_list:
        movie_dict = {'id': rec.id_movie,
                      'title': rec.title,
                      'year': rec.year,
                      'cinema': rec.cinema,
                      'cast': rec.cast,
                      'director': rec.director,
                      'filmtv': rec.filmtv
                     }
        out.append(movie_dict)

    response = {}
    response['result'] = 'success'
    response['payload'] = out

    return JsonResponse(response)


@ensure_csrf_cookie
def deletemovie(request):
    """ Delete Tvshow """

    response_data = {}
    response_data['result'] = 'success'
    movie_id = request.POST.get('id', '')
    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '')

    if not check_session(kanazzi, username, action='deletemovie', store=True):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    current_user = User.objects.filter(username=username)
    # Check existing votes
    tvrs = TvShowVote.objects.filter(tvshow=movie_id).exclude(user=current_user[0])

    if tvrs:
        vote_check = tvrs[0]
        response_data['message'] = 'Cannot delete %s. It has been voted by some kaeroeso !' % (vote_check.tvshow.title)
        response_data['result'] = 'failure'
    else:
        show_to_delete = TvShow.objects.filter(id_tv_show=movie_id)
        if show_to_delete:
            tvshow = show_to_delete[0]
            tvshow.delete()
            response_data['message'] = 'Tvshow with id=' + movie_id + " deleted succcessfully."
        else:
            response_data['result'] = 'failure'
            response_data['message'] = 'Cannot delete tvshow with id=' + movie_id + ". It does not exist!"

    return JsonResponse(response_data)


def create_update_vote(current_user, tvshow, vote_dict):
    """ Create Update vote """
    tvsv = TvShowVote.objects.filter(user=current_user, tvshow=tvshow[0])
    if not tvsv:
        tvsv = TvShowVote(vote=vote_dict['vote'], user=current_user, tvshow=tvshow[0], \
                          now_watching=vote_dict["nw"], season=vote_dict["season"], \
                          episode=vote_dict["episode"], comment=vote_dict['comment'])
        tvsv.save()

        if not vote_dict["nw"]:
            notification = Notification(
                type="new_vote", \
                title="%s has just voted for a movie..." % current_user.username, \
                message="Title: %s - Vote: %s " \
                % (tvshow[0].title, vote_dict["vote"]), username=current_user.username)
            notification.save()
    else:
        current_vote = tvsv[0]
        if vote_dict['giveup']:
            current_vote.delete()

            notification = Notification(
                type="give_up", \
                title="%s has just gave up to follow a movie" % current_user.username, \
                message="%s" % tvshow[0].title, username=current_user.username)
            notification.save()

        else:

            finished = False
            first_comment = False

            if current_vote.now_watching and not vote_dict["nw"]:
                finished = True

            if current_vote.comment == "" and vote_dict["comment"] != "":
                first_comment = True

            current_vote.vote = vote_dict['vote']
            current_vote.now_watching = vote_dict["nw"]
            current_vote.episode = vote_dict["episode"]
            current_vote.season = vote_dict["season"]
            current_vote.comment = vote_dict["comment"]
            current_vote.save()

            if finished:
                notification = Notification(
                    type="new_vote", \
                    title="%s has just voted for a movie..." % current_user.username, \
                    message="Title: %s - Vote: %s " \
                    % (tvshow[0].title, vote_dict["vote"]), username=current_user.username)
                notification.save()

            if first_comment:
                notification = Notification(
                    type="new_comment", \
                    title="%s has just set a comment for a movie..." % current_user.username, \
                    message="Title: %s - %s... " \
                    % (tvshow[0].title, vote_dict["comment"][:30]), username=current_user.username)
                notification.save()

    # print(vote_dict)
    if vote_dict["nw"] and str(vote_dict["season"]) == "1" and str(vote_dict["episode"]) == "1":
        notification = Notification(
            type="new_nw", \
            title="%s has just started to watch a movie..." % current_user.username, \
            message="Title: %s - S%s E%s " \
            % (tvshow[0].title, vote_dict["season"], vote_dict["episode"]), username=current_user.username)
        notification.save()


@ensure_csrf_cookie
def savemovienew(request):
    """ Save Movie New """

    response_data = {}
    response_data['result'] = 'success'

    id_movie = request.POST.get('id', '')
    title = request.POST.get('title', '')
    media = request.POST.get('media', '')
    link = request.POST.get('link', '')
    vote = request.POST.get('vote', '')
    type = request.POST.get('type', 'brand_new')
    tvshow_type = request.POST.get('tvshow_type', 'movie')
    serie_season = request.POST.get('serie_season', 1)
    director = request.POST.get('director', '')
    year = request.POST.get('year', '')
    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '')
    now_watch_sw = request.POST.get('nw', False)
    giveup_sw = request.POST.get('giveup', False)
    later_sw = request.POST.get('later', False)
    season = request.POST.get('season', 1)
    episode = request.POST.get('episode', 1)
    comment = request.POST.get('comment', '')
    uploaded_file = request.FILES.get('pic', '')
    poster_name = ''
    upload_file_res = {}

    print(id_movie)
    # print (title)
    # print (media)
    # print (type)

    if uploaded_file:
        print("A file has been uploaded... " + uploaded_file.name)
        temp_f_name = title + '_' + uploaded_file.name
        poster_name = safe_file_name(temp_f_name, uploaded_file.content_type)

    now_watch = False
    if now_watch_sw == "on":
        now_watch = True

    giveup = False
    if giveup_sw == "on":
        giveup = True

    later = False
    if later_sw == "on":
        later = True

    if not check_session(kanazzi, username, action='savemovienew', store=True):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    if not title or not media or not tvshow_type:
        response_data['result'] = 'failure'
        response_data['message'] = 'Missing required data: check title, media and type'
        return JsonResponse(response_data)

    current_tvshow = TvShow.objects.filter(id_tv_show=id_movie)
    current_user = User.objects.filter(username=username)[0]

    # Movie exists and the current user is not the owner
    if current_tvshow and username != current_tvshow[0].user.username:
        print("User not owner of the movie is voting...")
        data_vote = {'nw': now_watch,
                     'episode': episode,
                     'season': season,
                     'vote': vote,
                     'giveup': giveup,
                     'comment': comment
                    }

        tvshow = current_tvshow[0]

        if not later:
            create_update_vote(current_user, current_tvshow, data_vote)

        # New feature: to allow not movie owner to upload the poster, set a link and set the season

        tvshow.serie_season = serie_season
        tvshow.save()

        if uploaded_file:
            upload_file_res = upload_cover(request, poster_name)

        upload_res = upload_file_res.get('result', 'failure')
        if upload_res == 'failure':
            poster_name = ''
        else:
            tvshow.poster = poster_name

        if link:
            tvshow.link = link

        if upload_res != 'failure' or (tvshow.link == "" and link):
            tvshow.save()

            notification = Notification(
                type="new_movie", \
                title="%s has just added a new movie poster or a link" \
                % username, message="Title: %s" % title, username=username)
            notification.save()

        # End New feature

    else:
        if not current_tvshow:  # Movie does not exist

            if uploaded_file:
                upload_file_res = upload_cover(request, poster_name)

            upload_res = upload_file_res.get('result', 'failure')
            if upload_res == 'failure':
                poster_name = ''

            print("Adding tvshow... Title: " + title)

            tvshow = TvShow(title=title, media=media, link=link, vote=vote, user=current_user,
                            type=type, tvshow_type=tvshow_type,
                            director=director, year=year,
                            poster=poster_name, serie_season=serie_season)
            tvshow.save()

            if not later:
                tvsv = TvShowVote(
                    vote=vote,
                    user=current_user,
                    tvshow=tvshow,
                    now_watching=now_watch,
                    season=season,
                    episode=episode,
                    comment=comment
                )
                tvsv.save()

            notification = Notification(
                type="new_movie", \
                title="%s has just added a new movie" % username, \
                message="Title: %s" % title, username=username)
            notification.save()

            response_data['message'] = 'TvShow/Movie %s saved!' % title

        else:  # Movie exists and the owner is modifyng it

            if uploaded_file:
                upload_file_res = upload_cover(request, poster_name)

            upload_res = upload_file_res.get('result', 'failure')
            if upload_res == 'failure':
                poster_name = ''
            else:
                notification = Notification(
                    type="new_movie", \
                    title="%s has just added a new movie poster" % username, \
                    message="Title: %s" % title, username=username)
                notification.save()

            print("Updating tvshow... Title: " + title)
            tvshow = current_tvshow[0]
            tvshow.title = title
            tvshow.media = media
            tvshow.link = link
            tvshow.vote = vote
            tvshow.type = type
            tvshow.serie_season = serie_season
            tvshow.tvshow_type = tvshow_type
            tvshow.director = director
            tvshow.year = year
            if poster_name:
                tvshow.poster = poster_name
            tvshow.save()

            data_vote = {'nw': now_watch,
                         'episode': episode,
                         'season': season,
                         'vote': vote,
                         'giveup': giveup,
                         'comment': comment
                        }
            if not later:
                create_update_vote(current_user, current_tvshow, data_vote)

    response_data.update({"upload_result": upload_file_res})

    return JsonResponse(response_data)


def get_tvshows(request):
    """ Get Tvshow Old """

    response_data = {}
    username = request.POST.get('username', '')
    kanazzi = request.POST.get('kanazzi', '')

    if not username and not kanazzi:
        username = request.GET.get('username', '')
        kanazzi = request.GET.get('kanazzi', '')
        print("A client is using a deprecated GET method for get tv shows")

    if not check_session(kanazzi, username, action='gettvshows', store=False):
        response_data['result'] = 'failure'
        response_data['message'] = 'Invalid Session'
        return JsonResponse(response_data, status=401)

    response_data['result'] = 'success'
    out_list = []
    movies_list = TvShow.objects.filter().order_by('-created')

    for tvs in movies_list:
        # dt = tvs.created.strftime("%A, %d. %B %Y %I:%M%p")
        movie_created = tvs.created.strftime("%d %B %Y ")
        dtsec = time.mktime(tvs.created.timetuple())
        tvsv = TvShowVote.objects.filter(tvshow=tvs)
        avg_vote = 0
        valid_vote_count = 0
        u_v_dict = {}

        for tvshow_vote in tvsv:
            if not tvshow_vote.now_watching:
                avg_vote += tvshow_vote.vote
                valid_vote_count += 1
            us_dt = tvshow_vote.created.strftime("%A, %d. %B %Y %I:%M%p")
            str_vote = str(decimal.Decimal(tvshow_vote.vote))
            u_v_dict[tvshow_vote.user.username] = {
                'us_username': tvshow_vote.user.username,
                'us_name': tvshow_vote.user.name,
                'us_vote': str_vote, 'us_date': us_dt,
                'now_watching': tvshow_vote.now_watching,
                'episode': tvshow_vote.episode,
                'season': tvshow_vote.season,
                'comment': tvshow_vote.comment
            }

        if tvsv and avg_vote:
            avg_vote = float(avg_vote) / float(valid_vote_count)
        else:
            avg_vote = 0
        str_vote1 = str(decimal.Decimal(tvs.vote))
        avg_vote_str = "%.2f" % avg_vote
        movie_dict = {
            'title': tvs.title,
            'media': tvs.media,
            'vote': str_vote1,
            'username': tvs.user.username,
            'name': tvs.user.name,
            'poster': tvs.poster,
            'datetime_sec': dtsec,
            'u_v_dict': u_v_dict,
            'type': tvs.type,
            'director': tvs.director,
            'year': tvs.year,
            'id': tvs.id_tv_show,
            'link': tvs.link,
            'datetime': movie_created,
            'avg_vote': avg_vote_str,
            'serie_season': tvs.serie_season
        }
        out_list.append(movie_dict)

    vote_user_dict = {}
    vote_user = []
    all_votes = TvShowVote.objects.all()
    for tvshow_vote in all_votes:
        if tvshow_vote.user.username in vote_user_dict:
            vote_user_dict[tvshow_vote.user.username] += 1
        else:
            vote_user_dict[tvshow_vote.user.username] = 1
    for k in vote_user_dict:
        vote_user.append({'name': k, 'count': vote_user_dict[k]})

    payload = {'tvshows': out_list, 'votes_user': vote_user}

    response_data['payload'] = json.dumps(payload)
    return JsonResponse(response_data)


def get_movies_datatable(request):
    """ Get Tvshow for js datatable """
    movies_list = Movie.objects.all().exclude(cinema="")
    out = []
    for rec in movies_list:
        movie_dict = {
            '0': rec.title,
            '1': rec.year,
            '2': rec.cinema,
            '3': rec.cast,
            '4': rec.director,
            '5': rec.filmtv
        }
        out.append(movie_dict)

    response_data = {}
    response_data['result'] = 'success'
    response_data['data'] = out

    return JsonResponse(response_data)


def get_catalogue(request):
    """ Get Media Catalogue """
    response = {'result':'success'}

    try:
        i_data = json.loads(request.body)
        username = i_data.get('username', '')
        firebase_id_token = i_data.get('firebase_id_token', '')
        cat_type = i_data.get('cat_type', '')
        kanazzi = i_data.get('kanazzi', '')
    except (TypeError, ValueError):
        response['result'] = 'failure'
        response['message'] = 'Bad input format'
        return JsonResponse(response, status=400)

    if not check_session(kanazzi, username, action='get_catalogue', store=True):
        response['result'] = 'failure'
        response['message'] = 'Invalid Session'
        return JsonResponse(response, status=401)

    if not cat_type:
        media_cat = Catalogue.objects.all()
    else:
        media_cat = Catalogue.objects.filter(cat_type=cat_type)

    response['payload'] = [model_to_dict(rec) for rec in media_cat]

    return JsonResponse(response)
