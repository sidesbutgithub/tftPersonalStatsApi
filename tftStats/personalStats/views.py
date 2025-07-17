from adrf.views import APIView
from rest_framework.response import Response
from .utils import getPuuid, getPlayerLast20
import json

# Create your views here.
class last20View(APIView):
    async def get(self, request, **kwargs):
        try:
            res = await getPuuid(request, getPlayerLast20, **kwargs)
            return res

        except Exception as err:
            print(err)
            return Response(status=500)
    

class testView(APIView):
    def get(self, request):
        return Response({"test": "success"})