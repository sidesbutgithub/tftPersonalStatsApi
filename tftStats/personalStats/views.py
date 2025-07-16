from rest_framework import viewsets
from rest_framework.response import Response
from dotenv import dotenv_values
import requests
import json

# Create your views here.

class statsViewSet(viewsets.ViewSet):
    def list(self, request):
        data = json.loads(request.body.decode('utf-8'))
        apiKey = dotenv_values(".env")["RIOT_API_KEY"]
        try:
            reqUrl = f"https://{data['region']}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{data['playerID']}/{data['playerTag']}?api_key={apiKey}"
            res = requests.get(reqUrl)
            res.raise_for_status()

            puuid = res.json()["puuid"]

            reqUrl = f"https://{data['region']}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={apiKey}"
            res = requests.get(reqUrl)
            res.raise_for_status()
            matches = res.json()
            
            last20 = []
            for i in matches:
                reqUrl = f"https://{data['region']}.api.riotgames.com/tft/match/v1/matches/{i}?api_key={apiKey}"
                res = requests.get(reqUrl)
                res.raise_for_status()
                matchParticipants = res.json()['info']['participants']
                for j in matchParticipants:
                    if j['puuid'] == puuid:
                        last20.append(j['placement'])
                        break
            return Response(last20)

        except:
            print(Exception)