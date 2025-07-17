import json
from django.core.cache import cache
import requests
from dotenv import dotenv_values
from rest_framework.response import Response

async def getPuuid(request, next, **kwargs):
    puuid = cache.get(f"{kwargs['playerID']}#{kwargs['playerTag']}")
    if puuid:
        request.puuid = puuid
        return await next(request, **kwargs)
    reqUrl = f"https://{kwargs['region']}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{kwargs['playerID']}/{kwargs['playerTag']}?api_key={dotenv_values(".env")["RIOT_API_KEY"]}"
    res = requests.get(reqUrl)
    res.raise_for_status()
    puuid = res.json()["puuid"]
    cache.set(f"{kwargs['playerID']}#{kwargs['playerTag']}", puuid, timeout=None)
    request.puuid = puuid
    return await next(request, **kwargs)


async def getPlayerLast20(request, **kwargs):
    cachedStats = cache.get(f"{kwargs['playerID']}#{kwargs['playerTag']}_data")

    if cachedStats:
        return Response(json.loads(cachedStats))

    reqUrl = f"https://{kwargs['region']}.api.riotgames.com/tft/match/v1/matches/by-puuid/{request.puuid}/ids?start=0&count=20&api_key={dotenv_values(".env")["RIOT_API_KEY"]}"
    res = requests.get(reqUrl)
    res.raise_for_status()
    matches = res.json()

    last20 = []
    units = {}

    for i in matches:
        reqUrl = f"https://{kwargs['region']}.api.riotgames.com/tft/match/v1/matches/{i}?api_key={dotenv_values(".env")["RIOT_API_KEY"]}"
        res = requests.get(reqUrl)
        res.raise_for_status()
        matchParticipants = res.json()['info']['participants']
        for j in matchParticipants:
            if j['puuid'] == request.puuid:
                last20.append(j['placement'])
                for unit in j['units']:
                    unitName = f"{unit["character_id"]}-{unit["tier"]}"
                    if not(unitName in units):
                        units[unitName] = {"games": 0, "totalPlacement": 0}
                    units[unitName]['games'] += 1
                    units[unitName]['totalPlacement'] += j['placement']
                break

    cache.set(f"{kwargs['playerID']}#{kwargs['playerTag']}_data", json.dumps({"scores": last20, "units": units})) #default of 5 minute ttl
    return Response({"scores": last20, "units": units})