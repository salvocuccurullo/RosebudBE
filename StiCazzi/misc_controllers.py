import json
import base64
import os
import logging
import uuid

from random import randint
from datetime import datetime
import datetime as dttt
import Padding
import requests
from requests.auth import HTTPBasicAuth

import firebase_admin
from firebase_admin import credentials, auth
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import git

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from django.core import serializers
from django import get_version
from django.contrib.auth import authenticate

from StiCazzi.models import Pesata, Soggetto, Song, Lyric, Movie, User, Session, Location, Configuration, Notification, UserDevice
from StiCazzi.models import ConfigurationSerializer
from StiCazzi.env import MONGO_API_URL, MONGO_API_USER, MONGO_API_PWD, MONGO_SERVER_CERTIFICATE, MAX_FILE_SIZE
from . import utils

# def get_demo_json(request):
#     """
#     Controller:
#     """

#     response_data = {}
#     response_data['result'] = 'success'
#     response_data['message'] = 'hello world!'

#     return JsonResponse(response_data)

def get_songs(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'
    response_data['payload'] = serializers.serialize("json", Song.objects.all())

    return JsonResponse(response_data)


def get_lyrics_by_song(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'

    try:
        int(request.GET['id_song'])
    except ValueError:
        response_data['result'] = 'error'
        response_data['message'] = 'not valid id'
        return JsonResponse(response_data)

    songs = Song.objects.filter(id_song=request.GET['id_song'])

    if songs:
        song = songs[0]
        lyrics_list = Lyric.objects.all().filter(id_song_id=song.id_song)
        final_list = [{'id':rec.id_lyric, 'text':rec.lyric} for rec in lyrics_list]
        out = {'title':song.title, 'author':song.author, 'lyrics':final_list}
        response_data['message'] = json.dumps(out)
    else:
        response_data['message'] = 'song not found'

    return JsonResponse(response_data)

def get_movies(request):
    """
    Controller:
    """
    response_data = {}
    response_data['result'] = 'success'
    response_data['payload'] = serializers.serialize("json", Movie.objects.all())

    return JsonResponse(response_data)


def get_pesate_by_soggetto(request, id_soggetto):
    """
    Controller:
    """

    response_data = {}
    soggetti = Soggetto.objects.filter(id_soggetto=id_soggetto)

    if soggetti:
        soggetto = soggetti[0]
        lista_pesi = Pesata.objects.filter(id_soggetto=id_soggetto).filter(data__gte=dttt.date(2019,1,1))
        peso_list = []
        for peso in lista_pesi:
            peso_diz = {'data':peso.data.strftime("%d/%m/%y"), 'peso':peso.peso}
            peso_diz = utils.decimal_dumps(peso_diz)
            peso_list.append(peso_diz)
        response_data['message'] = {'nome': soggetto.nome,
                                    'cognome': soggetto.cognome,
                                    'pesate':peso_list}
    else:
        response_data['message'] = {}
    #peso_list = json.dumps(peso_list)

    response_data['result'] = 'success'

    return JsonResponse(response_data)

def get_all_pesate(request):
    """
    Controller:
    """

    out = {}
    soggetti = Soggetto.objects.values_list('id_soggetto', 'nome')
    for soggetto in soggetti:
        pesate = Pesata.objects.filter(id_soggetto=soggetto).filter(data__gte=dttt.date(2019,1,1))
        peso_list = []
        for peso in pesate:
            peso_diz = {'data':peso.data.strftime("%Y/%m/%d"), 'peso':peso.peso}
            peso_diz = utils.decimal_dumps(peso_diz)
            peso_list.append(peso_diz)

        out[soggetto[0]] = {}
        out[soggetto[0]]['nome'] = soggetto[1]
        out[soggetto[0]]['pesate'] = peso_list

    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = out

    return JsonResponse(response_data)

def get_sum_by_month(request):
    """
    Controller:
    """

    out = {}
    soggetti = Soggetto.objects.values_list('id_soggetto', 'nome')
    for soggetto in soggetti:
        pesate = Pesata.objects.filter(id_soggetto=soggetto[0]).filter(data__gte=dttt.date(2019,1,1))
        peso_list = []
        mesi_diz = {}
        for peso in pesate:
            mese_anno = peso.data.strftime("%Y%m")
            if mese_anno not in mesi_diz:
                mesi_diz[mese_anno] = {'pesi_mese':[]}
            mesi_diz[mese_anno]['pesi_mese'].append(peso.peso)
            mesi_diz[mese_anno]['last_data'] = peso.data.strftime("%Y/%m/%d")

        pesate = list(mesi_diz.keys())
        pesate.sort()

        for mese_anno in pesate:
            cum_peso = mesi_diz[mese_anno]['pesi_mese'][0] - mesi_diz[mese_anno]['pesi_mese'][-1]
            peso_diz = {'data':mesi_diz[mese_anno]['last_data'], 'peso':cum_peso}
            peso_diz = utils.decimal_dumps(peso_diz)
            peso_list.append(peso_diz)

        out[soggetto[0]] = {}
        out[soggetto[0]]['nome'] = soggetto[1]
        out[soggetto[0]]['pesate'] = peso_list

    response_data = {}
    response_data['result'] = 'success'
    response_data['message'] = out

    return JsonResponse(response_data)