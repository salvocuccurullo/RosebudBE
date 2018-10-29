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

from django.conf.urls import url
from django.contrib import admin
from StiCazzi import views, controllers, movies_controllers, covers_controllers

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.songs, name='index'),
    url(r'^showmovies/$', views.movies, name='movie'),
    url(r'^showpesi/$', views.peso, name='peso'),
    url(r'^showsongs/$', views.songs, name='song'),

    url(r'^songs/$', controllers.get_songs, name='index'),
    url(r'^randomSong$', controllers.get_random_song, name='index'),
    url(r'^song/$', controllers.get_lyrics_by_song, name='index'),
    url(r'^get_pesate_by_soggetto/(?P<id_soggetto>\d+)$', controllers.get_pesate_by_soggetto),
    url(r'^get_all_pesate/$', controllers.get_all_pesate),
    url(r'^getByMonth/$', controllers.get_sum_by_month),

    url(r'^getTvShows$', movies_controllers.get_tvshows),
    url(r'^getTvShows2$', movies_controllers.get_tvshows_new),
    url(r'^getTvShows3$', movies_controllers.get_tvshows_new_opt),
    url(r'^deletemovie$', movies_controllers.deletemovie),
    url(r'^savemovienew$', movies_controllers.savemovienew),
    url(r'^moviesdt/$', movies_controllers.get_movies_datatable, name='movie'),
    url(r'^moviesct/$', movies_controllers.get_movies_ct, name='movie'),

    url(r'^uploadcover$', covers_controllers.save_cover),
    url(r'^getcovers$', covers_controllers.get_covers),
    url(r'^getrandomcover$', covers_controllers.get_random_cover),
    url(r'^getremotecovers$', covers_controllers.get_remote_covers),
    url(r'^getcoversstats$', covers_controllers.get_covers_stats),

    url(r'^geolocation$', controllers.geolocation),
    url(r'^geolocation2$', controllers.geolocation2),
    url(r'^getcatalogue$', movies_controllers.get_catalogue),

    url(r'^login$', controllers.login),
    url(r'^setFBToken$', controllers.set_fb_token),
    url(r'^checkFBToken$', controllers.check_fb_token),

    url(r'^testSession$', controllers.test_session),
]
