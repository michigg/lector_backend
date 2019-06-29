from __future__ import unicode_literals

from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from lector.serializer import MovementTypeSerializer

'''
Author: Michael Götz
'''


@permission_classes((AllowAny,))
class ApiListMovementTypes(views.APIView):
    def get(self, request):
        results = MovementTypeSerializer([{'id': '0', 'name': 'Pedestrian'}, {'id': '1', 'name': 'Bicycle'}],
                                         many=True).data
        return Response(results, status=status.HTTP_200_OK)
