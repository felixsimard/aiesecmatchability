# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from matchability_lib.matchability import matchability


@api_view(['GET', 'POST'])
def opportunity_matchability(request):
    if request.method == 'GET':
        return Response({"message": "Hello, world!"})
        # return Response(request.data)
    elif request.method == 'POST':
        return Response(matchability(request.data))
        return Response(request.data)
