import json, random
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict
from StiCazzi.controllers import get_demo_json, get_lyrics_by_song
from StiCazzi.models import Song, Lyric, TvShow

def auth(request):

    if request.user.is_authenticated:
        return True
    else:
        # Redirection to login page to be implemented
        # OR
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = authenticate(username=username, password=password)
        if user == None:
            return False
        else: 
            return True

def index(request):

    if not auth(request):
        html = render_to_string('err_auth.html')
        return HttpResponse(html)
 
    m = []
    s = []
    tvshows = TvShow.objects.all()
    shows = [model_to_dict(rec) for rec in tvshows]
    for rec in shows:
        if rec.get('tvshow_type','') == "movie":
            #m.append({"title":rec.title, "media":rec.media})
            m.append(rec)
        elif rec.get('tvshow_type','') == "serie":
            s.append(rec)
            #s.append({"title":rec.title, "media":rec.media, "serie_season": rec.serie_season})
        else:
            pass
   
    m = sorted(m, key = lambda i: i['title'])
    s = sorted(s, key = lambda i: i['title'])
    
    html = render_to_string('home.html', {'movies': m, 'series': s})
    
    return HttpResponse(html)

def songs(request):

    if not auth(request):
        html = render_to_string('err_auth.html')
        return HttpResponse(html)

    song_list = Song.objects.all()
    
    if not song_list:
        html = render_to_string('empty.html', {'message': 'No songs available ! ;('})
    
    else:
        random_sel = random.randint(0, len(song_list)-1)
        song = song_list[random_sel]
        l = Lyric.objects.all().filter(id_song_id=song.id_song)
        
        if not l:
            lyrics = 'No lyrics available for this song.'
        else:
            k = ['<span id="lyric_%s">%s</span><br/>' % (rec.id_lyric, rec.lyric) for rec in l]                
            lyrics = ''.join(k)

        html = render_to_string('song.html', {'title': song.title, 'author': song.author, 'lyrics': lyrics})
        
    return HttpResponse(html)

def movies(request):
    
    if not auth(request):
        html = render_to_string('err_auth.html')
        return HttpResponse(html)
    
    html = render_to_string('movies.html')    
    
    return HttpResponse(html)    

def peso(request):

    if not auth(request):
        html = render_to_string('err_auth.html')
        return HttpResponse(html)

    html = render_to_string('peso.html')    

    return HttpResponse(html)

