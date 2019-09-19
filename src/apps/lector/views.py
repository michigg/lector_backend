from __future__ import unicode_literals

import datetime
import logging
import os

from django.conf import settings
from django.utils import timezone
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.lector.controllers import OSMController

logger = logging.getLogger(__name__)
'''
Author: Michael Götz
'''


@permission_classes((AllowAny,))
class ApiOpenSpacePlot(views.APIView):
    def get(self, request, file_name):
        osmm = OSMController()
        open_space = osmm.osp_config_c.get_open_space(file_name)
        if open_space:
            try:
                timestamp = os.path.getctime(f'{settings.MEDIA_ROOT}/{open_space.file_name}.svg')
                creation_time = datetime.datetime.fromtimestamp(timestamp, tz=timezone.get_current_timezone())
                max_creation_time = timezone.localtime(timezone.now()) - datetime.timedelta(
                    hours=settings.OPEN_SPACE_MAX_CACHING_TIME)

                if creation_time < max_creation_time:
                    osmm.create_complete_open_space_plot(open_space, settings.MEDIA_ROOT)
            except FileNotFoundError as err:
                osmm.create_complete_open_space_plot(open_space, settings.MEDIA_ROOT)

            return Response({"url": f'{settings.MEDIA_URL}{open_space.file_name}.svg'},
                            status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={'access-control-allow-origin': '*'})
