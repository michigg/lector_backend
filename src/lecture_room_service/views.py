from django.shortcuts import render

# Create your views here.
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from lecture_room_service.serializer import LectureSerializer
from lecture_room_service.utils.univis_lecture_room_controller import UnivISLectureController


@permission_classes((AllowAny,))
class ApiLectures(views.APIView):
    def get(self, request):
        search_token = request.GET.get('token', None)
        if search_token:
            univis_lecture_c = UnivISLectureController()
            lectures = univis_lecture_c.get_lectures_by_token(search_token)
            lectures_dicts = []
            for lecture in lectures:
                lectures_dicts.append(lecture.__dict__)
            results = LectureSerializer(lectures_dicts, many=True).data
            return Response(results, status=status.HTTP_200_OK, headers={'access-control-allow-origin': '*'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
