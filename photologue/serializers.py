from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from .models import Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'