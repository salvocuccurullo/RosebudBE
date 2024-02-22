"""
    StiCazzi URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/1.11/topics/http/urls/
    Examples:
    Function views
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
    Class-based views
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
    Including another URLconf
        1. Import the include() function: from django.conf.urls import url, include
        2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

#from django.conf.urls import url, include      # removed after 4.0 migration
from django.urls import re_path as url          # added after 4.0 migration
from django.urls import include
from django.contrib import admin
from StiCazzi import views, controllers, movies_controllers, covers_controllers, misc_controllers, albums_controllers

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^showmovies/$', views.movies, name='movie'),
    url(r'^showpesi/$', views.peso, name='peso'),
    url(r'^showsongs/$', views.songs, name='song'),

    url(r'^songs/$', misc_controllers.get_songs, name='index'),
    url(r'^randomSong$', controllers.get_random_song, name='index'),
    url(r'^song/$', misc_controllers.get_lyrics_by_song, name='index'),
    url(r'^get_pesate_by_soggetto/(?P<id_soggetto>\d+)$', misc_controllers.get_pesate_by_soggetto),
    url(r'^get_all_pesate/$', misc_controllers.get_all_pesate),
    url(r'^getByMonth/$', misc_controllers.get_sum_by_month),
    url(r'^getconfigs2$', controllers.get_configs_new),

    #url(r'^deletemovie$', movies_controllers.deletemovie),
    url(r'^savemovienew$', movies_controllers.savemovienew),
    url(r'^moviesct/$', movies_controllers.get_movies_ct, name='movie'),
    url(r'^setlike$', movies_controllers.setlike),

    url(r'^uploadcover$', covers_controllers.save_cover),
    url(r'^getcovers2$', covers_controllers.get_covers_ng),
    #url(r'^getrandomcover$', covers_controllers.get_random_cover),
    url(r'^getrandomcover$', albums_controllers.get_random_album),
    url(r'^getcoversstats$', covers_controllers.get_covers_stats),
    url(r'^spotify$', covers_controllers.spotify),
    url(r'^spotifysearch$', covers_controllers.spotify_search),
    url(r'^localsearch2$', covers_controllers.get_covers_by_search_ng),

    url(r'^geolocation$', controllers.geolocation),
    url(r'^geolocation2$', controllers.geolocation2),
    url(r'^getcatalogue$', movies_controllers.get_catalogue),

    url(r'^login$', controllers.login),
    url(r'^logout$', controllers.logout),
    url(r'^setFBToken2$', controllers.set_fb_token2),
    url(r'^refreshtoken$', controllers.refresh_token),

    url(r'^version', controllers.version),
    url(r'^commit', controllers.get_last_commit),

# new endpoint

    url(r'^api/randomSong$', controllers.get_random_song, name='index'),
    url(r'^api/getconfigs2$', controllers.get_configs_new),

    url(r'^api/getTvShowsList$', movies_controllers.get_tvshows_list),
    url(r'^api/getShow$', movies_controllers.getShow),
    #url(r'^api/deletemovie$', movies_controllers.deletemovie),
    url(r'^api/savemovienew$', movies_controllers.savemovienew),
    url(r'^api/moviesct/$', movies_controllers.get_movies_ct, name='movie'),
    url(r'^api/setlike$', movies_controllers.setlike),
    url(r'^api/ustats', movies_controllers.get_user_stats),

    url(r'^api/uploadcover$', covers_controllers.save_cover),
    url(r'^api/getcovers2$', covers_controllers.get_covers_ng),
    #url(r'^api/getrandomcover$', covers_controllers.get_random_cover),
    url(r'^api/getrandomcover$', albums_controllers.get_random_album),
    #url(r'^api/getcoversstats$', covers_controllers.get_covers_stats),
    url(r'^api/getcoversstats$', albums_controllers.get_stats),
    url(r'^api/spotify$', covers_controllers.spotify),
    url(r'^api/spotifysearch$', covers_controllers.spotify_search),
    url(r'^api/localsearch2$', covers_controllers.get_covers_by_search_ng),

    url(r'^api/geolocation$', controllers.geolocation),
    url(r'^api/geolocation2$', controllers.geolocation2),
    url(r'^api/getcatalogue$', movies_controllers.get_catalogue),
    url(r'^api/getmediastats$', movies_controllers.getMediaStats),

    url(r'^api/login$', controllers.login),
    url(r'^api/logout$', controllers.logout),
    url(r'^api/fblogin$', controllers.fblogin),
    url(r'^api/setFBToken2$', controllers.set_fb_token2),
    url(r'^api/refreshtoken$', controllers.refresh_token),

    url(r'^api/version', controllers.version),
    url(r'^api/commit', controllers.get_last_commit),

    url(r'^api/getAlbums', albums_controllers.get_albums),
    url(r'^api/getTracks', albums_controllers.get_tracks),
    url(r'^api/getSpotifyAlbumsXArtist', albums_controllers.get_spotify_albums_x_artist),
    url(r'^api/getSpotifyArtists', albums_controllers.get_spotify_artists),
    url(r'^api/getSpotifyTracks', albums_controllers.get_spotify_tracks),
    url(r'^api/setRemarkable', albums_controllers.set_remarkable),
    url(r'^api/getRandomAlbum', albums_controllers.get_random_album),
    url(r'^api/addTrack', albums_controllers.add_track),
    url(r'^api/getOneTrack', albums_controllers.get_one_track),
    url(r'^api/setOneTrack', albums_controllers.set_one_track),
    url(r'^api/deleteTrack', albums_controllers.delete_track),
    url(r'^api/addAlbum', albums_controllers.add_album),
    url(r'^api/getOneAlbum', albums_controllers.get_one_album),
    url(r'^api/setOneAlbum', albums_controllers.set_one_album),
    url(r'^api/deleteOneAlbum', albums_controllers.delete_one_album),
    url(r'^api/getStats', albums_controllers.get_stats),
]
