from django.db import models
from unittest.util import _MAX_LENGTH
from datetime import *
from rest_framework import serializers

class Soggetto(models.Model):
    id_soggetto = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    data_nascita = models.DateField()


class Pesata(models.Model):
    id_pesata = models.AutoField(primary_key=True)
    data = models.DateField()
    peso = models.DecimalField(max_digits=4, decimal_places=1)
    note = models.CharField(max_length=50)
    id_soggetto = models.ForeignKey(Soggetto, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('data', 'id_soggetto')


class Song(models.Model):
    id_song = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=100)
    spotify = models.CharField(max_length=400, default='')
    youtube = models.CharField(max_length=400, default='')
    deezer = models.CharField(max_length=400, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Lyric(models.Model):
    id_lyric = models.AutoField(primary_key=True)
    lyric = models.CharField(max_length=400)
    id_song = models.ForeignKey(Song, on_delete=models.CASCADE)


class Movie(models.Model):
    id_movie = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    year = models.IntegerField()
    director = models.CharField(max_length=150)
    cinema = models.CharField(max_length=100)
    cast = models.CharField(max_length=500)
    filmtv = models.CharField(max_length=10)


class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, null=False, unique=True)
    password = models.CharField(max_length=100, null=False, default='')
    email = models.CharField(max_length=200, null=False, default='')
    name = models.CharField(max_length=300)
    surname = models.CharField(max_length=150)
    birth_date = models.DateField()
    poweruser = models.BooleanField(default=False)
    geoloc_enabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class UserDevice(models.Model):
    id_user_device = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=300, null=False, default='')
    rosebud_id = models.CharField(max_length=300, null=False, default='')
    device_version = models.CharField(max_length=300, null=False, default='')
    device_platform = models.CharField(max_length=300, null=False, default='')
    app_version = models.CharField(max_length=300, null=False, default='')
    fcm_token = models.CharField(max_length=300, null=False, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Mp3(models.Model):
    id_mp3 = models.AutoField(primary_key=True)
    title = models.CharField(max_length=300)
    media = models.CharField(max_length=150)
    path = models.CharField(max_length=150)
    note = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['title'], name='title_idx_mp3'),
        ]


class TvShow(models.Model):
    id_tv_show = models.AutoField(primary_key=True)
    title = models.CharField(max_length=300)
    media = models.CharField(max_length=150)
    type = models.CharField(max_length=150, default='brand_new')
    tvshow_type = models.CharField(max_length=150, default='movie')
    director = models.CharField(max_length=150, default='')
    serie_season = models.PositiveSmallIntegerField(default=1)
    miniseries = models.BooleanField(default=False)
    year = models.IntegerField(default=0)
    link = models.CharField(max_length=400, default='')
    vote = models.DecimalField(max_digits=4, decimal_places=2, default=5)
    poster = models.CharField(max_length=300, default='')
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['title'], name='title_idx'),
        ]


class Minchiate(models.Model):
    id_minchiata = models.AutoField(primary_key=True)
    type = models.CharField(max_length=300)
    text = models.CharField(max_length=500)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)


class TvShowVote(models.Model):
    id_vote = models.AutoField(primary_key=True)
    vote = models.DecimalField(max_digits=4, decimal_places=2, default=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tvshow = models.ForeignKey(TvShow, on_delete=models.CASCADE)
    now_watching = models.BooleanField(default=False)
    season = models.PositiveSmallIntegerField(default=1)
    episode = models.PositiveSmallIntegerField(default=1)
    comment = models.CharField(max_length=500, default='')
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

class Like(models.Model):
    id_like = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_vote = models.ForeignKey(TvShowVote, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=50, default='')
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

class Session(models.Model):
    id_session = models.AutoField(primary_key=True)
    session_string = models.CharField(max_length=300)
    username = models.CharField(max_length=100, null=False)
    action = models.CharField(max_length=100, default='')
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_string'], name='session_idx'),
        ]


class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=300, null=False)
    message = models.CharField(max_length=300, null=False)
    username = models.CharField(max_length=100, null=False)
    sent = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['sent'], name='notif_sent_idx'),
        ]


class Catalogue(models.Model):
    id_cat = models.AutoField(primary_key=True)
    cat_type = models.CharField(max_length=100, null=False, default="unassigned")
    name = models.CharField(max_length=100, null=False)
    label = models.CharField(max_length=300, null=False)
    extra = models.CharField(max_length=500, null=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='catalogue_name_idx'),
        ]


class Location(models.Model):
    id_location = models.AutoField(primary_key=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.CharField(max_length=400, default='', null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='location_idx'),
        ]

class Configuration(models.Model):
    id_config = models.AutoField(primary_key=True)
    config_type = models.CharField(max_length=100, null=False, default="unassigned")
    name = models.CharField(max_length=100, null=False)
    value = models.CharField(max_length=300, null=False)
    extra = models.CharField(max_length=500, null=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='configuration_name_idx'),
        ]

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ('config_type','name','value')
