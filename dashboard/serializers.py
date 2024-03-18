from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Collection, Movies


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "first_name", "is_active"]


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ("title", "description", "movies")


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        fields = ("title", "description", "genres", "uuid")
