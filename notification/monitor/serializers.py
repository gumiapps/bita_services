from rest_framework import serializers
from rest_framework_api_key.models import APIKey

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'prefix', 'created', 'revoked']
