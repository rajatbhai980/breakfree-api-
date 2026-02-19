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

class RoomSerializer(serializers.ModelSerializer):
    room_authenticated = serializers.BooleanField(required=False) 
    class Meta: 
        model = Room
        fields = ['host', 'room_name', 'genre', 'participants', 'description', 'password', 'private', 'created', 'updated', 'room_authenticated']

class HomePageSerializer(serializers.Serializer): 
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    next_page_number = serializers.IntegerField()
    previous_page_number = serializers.IntegerField()
    genres = GenreSerializer(many=True)
    genre_name = serializers.CharField()
    rooms = RoomSerializer(many=True)
    is_authenticated = serializers.BooleanField()

class RegisterSerializer(serializers.ModelSerializer): 
    password2 = serializers.CharField()
    class Meta: 
        model = User
        fields = ["username", "email", "password", "password2"]
    
    def validate(self, data): 
        if data['password'] != data['password2']: 
            raise serializers.ValidationError('Passwords dont match each other')
        data.pop('password2')
        return data 
        
    def create(self, validated_data): 
        if User.objects.filter(username=validated_data['username']).exists(): 
            raise serializers.ValidationError('User with that username already exists!')
        user = User.objects.create_user(**validated_data)
        user.save()
        return user 