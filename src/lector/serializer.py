from rest_framework import serializers


class MovementTypeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, max_length=1)
    name = serializers.CharField(read_only=True, max_length=100)
