from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View 
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .models import Room, Friend, PendingRequest, Counter, Genre
from itertools import groupby
from django.utils import timezone
from django.db.models import F, fields, ExpressionWrapper, Q, Exists, OuterRef, Count
from django.db.models.functions import TruncSecond
from datetime import datetime
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response 
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken 
from .pagination import SearchResultPaginator
from rest_framework.generics import ListAPIView


#for getting the user model 
User = get_user_model()

# Create your views here.
@api_view(['GET'])
def home(request):
    if request.user.is_authenticated: 
        Friends = Friend.objects.select_related('friend2').filter(friend1 = request.user)
        friendList = []
        genres = Genre.objects.all()
        genre_name = request.GET.get('genre')
        for friendRow in Friends: 
            friendList.append(friendRow.friend2)
        rooms = Room.objects.filter( Q(host__in=friendList) | Q(host=request.user)).annotate(room_authenticated=Exists(
            Room.participants.through.objects.filter(
                room_id=OuterRef('pk'),
                user_id=request.user.pk
            )
        ))
        if genre_name == None: 
            genre_name = ""
        if genre_name: 
            genre = Genre.objects.get(name=genre_name)
            rooms = rooms.filter(genre=genre)
        page_number = request.GET.get('page')
        pages = Paginator(rooms, 3)
        curr_page = pages.get_page(page_number)
        next_page = curr_page.next_page_number() if curr_page.has_next() else -1 
        previous_page = curr_page.previous_page_number() if curr_page.has_previous() else -1 
        data = {
            "has_next": curr_page.has_next(), 
            "has_previous": curr_page.has_previous(), 
            "next_page_number": next_page, 
            "previous_page_number": previous_page, 
            "genres": genres, 
            "genre_name": genre_name, 
            "rooms": curr_page.object_list,
            "is_authenticated": request.user.is_authenticated, 
        }
        serializer = HomePageSerializer(data)
        return Response(serializer.data)
    return Response(status=status.HTTP_200_OK)

class Register(APIView):  
    def post(self, request): 
        regis_data = RegisterSerializer(data=request.data)
        if regis_data.is_valid():
            regis_data.save() 
            return Response(regis_data.data, status=status.HTTP_201_CREATED)
        else: 
            return Response(regis_data.errors, status=status.HTTP_400_BAD_REQUEST)
        
class Login(APIView): 
    '''
        jwt token setup is ready but using rest session for development 
        will use it after the project is done 
    '''
    def post(self, request): 
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user: 
            token = RefreshToken.for_user(user)
            return Response({
                "access_token": str(token.access_token), 
                "refresh_token": str(token)
            }, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class ProfilePage(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = Profile.objects.get(user=user)
        is_friend = user.friendModel.filter(
            friend2 = request.user
        ).exists()
        pending = PendingRequest.objects.filter(
            sender = request.user, 
            receiver = user
        ).exists()
        friend_count = Friend.objects.filter(friend1 = user).count()
        profile.is_friend = is_friend 
        profile.pending = pending 
        profile.friend_count = friend_count 
        serializer = ProfilePageSerailizer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EditProfile(APIView): 
    def get(self, request): 
        '''
        Single Serializer instead of nested serializer 
        Parent model handled by child serializer 
        '''
        if request.user.is_authenticated: 
            profile = request.user.profile
            serializer = EditProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        '''
        Seperate Serializer to keep logic explicit 
        Simple and easier to handle debug 
        '''
        if request.user.is_authenticated: 
            user_instance = User.objects.get(username=request.user)
            profile_instance = Profile.objects.get(user=request.user)
            user_serializer = UserSerializer(user_instance, data=request.data.get('user', {}), partial=True)
            profile_serializer = MinimalProfileSerializer(profile_instance, data=request.data.get('profile', {}), partial=True)
            if user_serializer.is_valid() and profile_serializer.is_valid(): 
                user_serializer.save()
                profile_serializer.save()
                return Response(status=status.HTTP_200_OK)
            else: 
                errors = {}
                errors.update(user_serializer.errors)
                profile_serializer.is_valid()
                errors.update(profile_serializer.errors)
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
class RoomViewSet(viewsets.ModelViewSet): 
    '''
    All of the room method are here
    Create Room - get without pk 
    Update Room - patch with pk 
    !!! if you try patch using drf its gonna prefill some fields
    like genre, private it will contradict our business logic 
    '''
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


@api_view(['GET'])
@login_required
def room(request, pk):
    '''
    return's Rooms information 
    counting - a boolean value to show start or stop button for the current user
    leaderboard showing user and their timesince they started the counter  
    participants - those who have entered the room 
    '''
    login_url = '/login/'
    room_info = Room.objects.get(pk=pk) 
    room_info.participants.add(request.user)
    participants = room_info.participants.all()
    room_counts = Counter.objects.select_related(
        "user").filter(
            room=room_info).annotate(
                raw_timesince=ExpressionWrapper(
                    (timezone.now() - F('created_at')), output_field=fields.DurationField()), rank=Count('user', distinct=True)).order_by('-raw_timesince')[:10]
    
    counting = Counter.objects.filter(user=request.user, room=room_info).exists()
    data = {
        'room_info': room_info, 
        'participants': participants, 
        'leaderboard': room_counts, 
        'counting': counting 
    }

    serializers = NestedRoomSerializer(data)
    return Response(serializers.data, status=status.HTTP_200_OK)

class ViewAllGenre(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

'''
    Friend request 
'''
@api_view(['POST'])
def create_friend_request(request, pk): 
    sender = request.user
    receiver = User.objects.get(pk=pk)
    PendingRequest.objects.create(
        sender = sender, 
        receiver = receiver
    )
    return Response(status=status.HTTP_201_CREATED)

@api_view(['GET'])
def view_friend_request(request): 
    pending_receiver_requests = PendingRequest.objects.select_related('sender').filter(receiver = request.user)
    requests = []
    for pending_receiver_request in pending_receiver_requests: 
        requests.append(pending_receiver_request.sender)
    serializer = PendingRequestSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST']) 
def accept_friend_request(request, pk): 
    sender = User.objects.get(pk=pk)
    #a to be relation 
    Friend.objects.create(
        friend1 = request.user,
        friend2 = sender
    )
    Friend.objects.create(
        friend1 = sender, 
        friend2 = request.user
    )

    pending_row = sender.friendRequestFrom.get(receiver=request.user)
    pending_row.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST']) 
def reject_friend_request(request, pk): 
    Sender = User.objects.get(pk = pk)
    pending_row = Sender.friendRequestFrom.get(receiver=request.user)
    pending_row.delete()
    messages.success(request, 'Request Deleted!')
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def remove_friend(request, pk): 
    friend = User.objects.get(pk=pk)
    friend_rows = Friend.objects.filter(Q(friend1=friend, friend2=request.user)| Q(friend1=request.user, friend2=friend)) 
    friend_rows.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def view_friend_list(request): 
    Friends = Friend.objects.select_related('friend2').filter(friend1 = request.user)
    friendList = []
    for friendRow in Friends: 
        friendList.append(friendRow.friend2)
    serializer = FriendListSerializer(friendList, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class SearchFriend(ListAPIView): 
    def get_queryset(self): 
        queryset = User.objects.all()
        search = self.request.query_params.get('search')
        if search is not None: 
            queryset = queryset.filter(Q(username__icontains=search)|Q(first_name__icontains=search)|Q(last_name__icontains=search))
        return queryset 
    serializer_class = SearchResultSerializer
    pagination_class = SearchResultPaginator
         

'''
Counting and leaderboard logic here
'''
@api_view(['POST'])
def start_counter(request, pk): 
    Counter.objects.create(
        user = request.user, 
        room = Room.objects.get(pk=pk)
    )
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def stop_counter(request, pk): 
    count_object = Counter.objects.filter(user=request.user, room=Room.objects.get(pk=pk))
    count_object.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def view_leaderboard(request, pk): 
    room = Room.objects.get(pk=pk)
    room_counts = Counter.objects.select_related(
        "user").filter(
            room=room).annotate(
                raw_timesince=ExpressionWrapper(
                    (timezone.now() - F('created_at')), output_field=fields.DurationField())).order_by('-raw_timesince')
    serializers = LeaderBoardSerializer(room_counts, many=True)
    return Response(serializers.data, status=status.HTTP_200_OK)

class RoomAuthorize(APIView): 
    def post(self, request, pk): 
        room_form = RoomAuthorizationSerializer(data=request.data)
        room = Room.objects.get(pk=pk)
        if room_form.is_valid(): 
            password = room_form.validated_data['password']
            room_password = room.password
            if password == room_password: 
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def room_participants(request, pk): 
    room = Room.objects.get(pk=pk)
    #moderator group creation/fetch
    groupName = f"{room.room_name}_moderators"
    moderators, created = Group.objects.get_or_create(name=groupName)
    is_private = room.private
    is_user_host = request.user == room.host
    is_user_moderator = moderators.user_set.filter(pk=request.user.pk).exists()
    participants = room.participants.all().annotate(is_moderator=Exists(
        moderators.user_set.filter(pk=OuterRef('pk'))
        #how does it know pk is of the user 
    ))
    data = {'participants': participants, 'room_name': room.room_name, 'is_room_private': is_private, 'is_user_host':is_user_host, 'is_user_moderator': is_user_moderator}
    serializers = ParticipantsPageSerializer(data)
    return Response(serializers.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_moderator(request, room_pk, user_pk):
    room = Room.objects.get(pk = room_pk)
    candidate = User.objects.get(pk = user_pk)

    groupName = f"{room.room_name}_moderators"
    group, _ = Group.objects.get_or_create(name=groupName)
    
    candidate.groups.add(group)
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def remove_moderator(request, room_pk, user_pk): 
    room = Room.objects.get(pk=room_pk)
    candidate = User.objects.get(pk=user_pk)

    groupName = f"{room.room_name}_moderators"
    group = Group.objects.get(name=groupName)

    candidate.groups.remove(group)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def remove_participant(request, room_pk, user_pk): 
    room = Room.objects.get(pk=room_pk)
    user = User.objects.get(pk=user_pk)

    #if user was a moderator 
    groupName = f"{room.room_name}_moderators"
    group = Group.objects.filter(name=groupName).first()
    if group and group.user_set.filter(pk=user.pk): 
        group.user_set.remove(user)

    room.participants.remove(user)
    return Response(status=status.HTTP_404_NOT_FOUND)

