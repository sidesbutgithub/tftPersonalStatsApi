from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from dotenv import dotenv_values
import requests
import json

# Create your views here.
class last20View(APIView):
    def get(self, request):
        data = json.loads(request.body.decode('utf-8'))
        apiKey = dotenv_values(".env")["RIOT_API_KEY"]
        try:
            puuid = cache.get(f"{data['playerID']}#{data['playerTag']}")
            
            if not puuid:
                reqUrl = f"https://{data['region']}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{data['playerID']}/{data['playerTag']}?api_key={apiKey}"
                res = requests.get(reqUrl)
                res.raise_for_status()
                puuid = res.json()["puuid"]
                cache.set(f"{data['playerID']}#{data['playerTag']}", puuid, timeout=None)

            cachedStats = cache.get(f"{data['playerID']}#{data['playerTag']}_data")

            if cachedStats:
                return Response(json.loads(cachedStats))


            reqUrl = f"https://{data['region']}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={apiKey}"
            res = requests.get(reqUrl)
            res.raise_for_status()
            matches = res.json()

            last20 = []
            units = {}

            for i in matches:
                reqUrl = f"https://{data['region']}.api.riotgames.com/tft/match/v1/matches/{i}?api_key={apiKey}"
                res = requests.get(reqUrl)
                res.raise_for_status()
                matchParticipants = res.json()['info']['participants']
                for j in matchParticipants:
                    if j['puuid'] == puuid:
                        last20.append(j['placement'])
                        for unit in j['units']:
                            unitName = f"{unit["character_id"]}-{unit["tier"]}"
                            if not(unitName in units):
                                units[unitName] = {"games": 0, "totalPlacement": 0}
                            units[unitName]['games'] += 1
                            units[unitName]['totalPlacement'] += j['placement']
                        break

            cache.add(f"{data['playerID']}#{data['playerTag']}_data", json.dumps({"scores": last20, "units": units})) #default of 5 minute ttl
            return Response({"scores": last20, "units": units})

        except:
            if res:
                print(res)
            print(Exception)