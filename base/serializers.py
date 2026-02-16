from rest_framework import serializers
from django.contrib.auth.models import User
from .models import * 

class ProfileSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Profile
        fields = "__all__"

class FriendSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Friend
        fields = "__all__"
class PendingSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = PendingRequest
        fields = "__all__"

class ProfilePageSerializer(serializers.ModelSerializer):
    friend_count = serializers.IntegerField()
    is_friend = serializers.BooleanField()
    pending = serializers.BooleanField()
    class Meta: 
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "friend_count", 'is_friend', "pending"]


class GenreSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Genre
        fields = "__all__"
        
class HomePageSerializer(serializers.Serializer): 
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    next_page_number = serializers.BooleanField()
    previous_page_number = serializers.BooleanField()
    genres = GenreSerializer(many=True)
    genre_name = serializers.CharField()
    is_authenticated = serializers.BooleanField()
