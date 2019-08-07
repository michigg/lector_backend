import logging

from rest_framework import serializers
from rest_framework.fields import Field

logger = logging.getLogger(__name__)


class LonLatSerializer(serializers.Serializer):
    longitude = serializers.FloatField(read_only=True)
    latitude = serializers.FloatField(read_only=True)


class LectureTypeField(Field):
    def to_representation(self, value):
        return {'id': value.name, 'value': value.value}


class RoomSerializer(serializers.Serializer):
    univis_key = serializers.CharField(read_only=True, max_length=100)
    building_key = serializers.CharField(read_only=True, max_length=100)
    number = serializers.IntegerField()
    level = serializers.IntegerField()


class LectureTermSerializer(serializers.Serializer):
    starttime = serializers.DateTimeField()
    endtime = serializers.DateTimeField()
    room = RoomSerializer()


class PersonSerializer(serializers.Serializer):
    univis_key = serializers.CharField(read_only=True, max_length=100)
    title = serializers.CharField(read_only=True, max_length=100)
    first_name = serializers.CharField(read_only=True, max_length=100)
    last_name = serializers.CharField(read_only=True, max_length=100)


class LectureSerializer(serializers.Serializer):
    univis_key = serializers.CharField(read_only=True, max_length=1)
    name = serializers.CharField(read_only=True, max_length=100)
    type = LectureTypeField(read_only=True)
    orgname = serializers.CharField(read_only=True, max_length=100)
    terms = LectureTermSerializer(many=True)
    lecturers = PersonSerializer(many=True)
    parent_lecture_ref = serializers.CharField(read_only=True, max_length=100)
    parent_lecture = serializers.CharField(read_only=True, max_length=100)


class SplittedLectureSerializer(serializers.Serializer):
    before = LectureSerializer(read_only=True, many=True)
    after = LectureSerializer(read_only=True, many=True)
