from rest_framework import serializers
from django.contrib.auth.models import User
from .models import * 

class FriendSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Friend
        fields = "__all__"
class PendingSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = PendingRequest
        fields = "__all__"

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]

class MinimalProfileSerializer(serializers.ModelSerializer): 
    '''
    this one is for showing some info for the profile page only 
    unlike the full fields version which is for editing 
    '''
    class Meta: 
        model = Profile 
        fields = ["bio", "phone_no", "profile_pic"]

class ProfilePageSerailizer(serializers.ModelSerializer): 
    user = ProfileUserSerializer()
    friend_count = serializers.IntegerField()
    is_friend = serializers.BooleanField()
    pending = serializers.BooleanField()
    class Meta: 
        model = Profile
        fields = ["user", "bio", "phone_no", "profile_pic", "friend_count", 'is_friend', "pending"]

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
    password2 = serializers.CharField(write_only=True)
    class Meta: 
        model = User
        fields = ["username", "email", "password", "password2"]    
    
    def validate(self, data): 
        if data['password'] != data['password2']: 
            raise serializers.ValidationError('Passwords must match each other')
        if data['email'] == "": 
            raise serializers.ValidationError('Pl')
        return data
        
    def create(self, validated_data): 
        validated_data.pop('password2')
        if User.objects.filter(username=validated_data['username']).exists(): 
            raise serializers.ValidationError('User with that username already exists!')
        user = User.objects.create_user(**validated_data)
        return user 

class UserSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = User
        fields = ["username", "email"]

class EditProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta: 
        model = Profile
        fields = ["user", "bio", "phone_no", "profile_pic"]

class CreateRoomSerializer(serializers.ModelSerializer): 
    host = serializers.PrimaryKeyRelatedField(queryset=User, default=serializers.CurrentUserDefault())
    genre_name = serializers.CharField(write_only=True, allow_blank=True, required=False)
    class Meta: 
        model = Room 
        exclude = ["created", "updated", "participants"]

    def create(self, validated_data): 
        has_genre = 'genre_name' in validated_data
        if has_genre: 
            genre, created = Genre.objects.get_or_create(name=validated_data['genre_name'])
            validated_data.pop('genre_name')
        if 'password' in validated_data: 
            validated_data['private'] = True 
        room = Room.objects.create(**validated_data)
        if has_genre: 
            room.genre = genre  
        room.participants.add(room.host)
        room.save()
        return room 
    
#serializers for reading rooms 
class ReadRoomSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Room
        fields = ['room_name', 'description']

    
class ReadRoomUsersSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = User
        fields = ['id', 'username']

class LeaderBoardSerializer(serializers.ModelSerializer): 
    rank = serializers.IntegerField()
    user = ReadRoomUsersSerializer()
    raw_timesince = serializers.DurationField()
    class Meta: 
        model = Counter
        fields = ['rank', 'user', 'raw_timesince']

class NestedRoomSerializer(serializers.Serializer): 
    room_info = ReadRoomSerializer()
    participants = ReadRoomUsersSerializer(many=True)
    leaderboard = LeaderBoardSerializer(many=True)
    counting = serializers.BooleanField()

