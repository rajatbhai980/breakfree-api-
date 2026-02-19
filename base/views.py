from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .forms import EditUserProfile, EditUser, CreateRoomForm, RoomAuthorizationForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .models import Room, Friend, PendingRequest, Counter, Genre
from itertools import groupby
from django.utils import timezone
from django.db.models import F, fields, ExpressionWrapper, Q, Exists, OuterRef
from django.db.models.functions import TruncSecond
from datetime import datetime
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response 
from rest_framework import status


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
    def post(self, request, *args, **kwargs): 
        regis_data = RegisterSerializer(data=request.data)
        if regis_data.is_valid():
            regis_data.save() 
            return Response(regis_data.data, status=status.HTTP_201_CREATED)
        else: 
            return Response(regis_data.errors)
        
class Login(APIView): 
    def get(self, request, *args, **kwargs): 
        pass        

    def post(self, request, *args, **kwargs): 
        pass

def logout_user(request): 
    logout(request)
    messages.success(request, "You have sucessfully logged out!")
    return redirect('home')

class Profile(APIView):
    def get(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        is_friend = user.friendModel.filter(
            friend2 = request.user
        ).exists()
        pending = PendingRequest.objects.filter(
            sender = request.user, 
            receiver = user
        ).exists()
        friend_count = Friend.objects.filter(friend1 = user).count()
        user.is_friend = is_friend 
        user.pending = pending 
        user.friend_count = friend_count 

        serializer = ProfilePageSerializer(user)
        return Response(serializer.data)
        # required things
        # isfriend 
        # pending 
        


class EditProfile(View): 
    def get(self, request, pk, *args, **kwargs): 
        profile = request.user.profile
        user_form = EditUser(instance=request.user)
        profile_form = EditUserProfile(instance=profile)
        context = {'user_form': user_form, 'profile_form': profile_form}
        return render(request, 'base/edit_profile.html', context)

    def post(self, request, pk, *args, **kwargs):
        profile = request.user.profile
        user_form = EditUser(request.POST, instance=request.user)
        profile_form = EditUserProfile(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid(): 
            user_form.save()
            profile_form.save()

        context = {'user_form': user_form, 'profile_form': profile_form}
        return render(request, 'base/edit_profile.html', context)
    
class CreateRoom(LoginRequiredMixin, View): 
    login_url ='/login/'
    def get(self, request, *args, **kwargs): 
        room = Room(host=request.user)
        room_form = CreateRoomForm(instance=room)
        genres = Genre.objects.all()
        context = {'room_form': room_form, 'genres': genres}
        return render(request, "base/create_room.html", context)

    def post(self, request, *args, **kwargs):
        post_data = request.POST.copy()
        
        genre_name = post_data.get('genre_name')
        if genre_name: 
            genre, created = Genre.objects.get_or_create(name=genre_name)
            post_data['genre'] = genre
        
        room_form = CreateRoomForm(post_data)
        genres = Genre.objects.all()
        if room_form.is_valid():
            room = room_form.save(commit=False)
            room.host = request.user
            password = room.password
            if password: 
                room.private = True
            room.save()
            room_pk = room.pk
            messages.success(request, "You have created a room. ")
            return redirect("room", pk=room_pk)
            
        context = {'room_form': room_form, 'genres': genres}
        return render(request, "base/create_room.html", context)    

    
@login_required
def room(request, pk):
    room_info = Room.objects.get(pk=pk) 
    room_info.participants.add(request.user)
    participants = room_info.participants.all()
    login_url = '/login/'
    room_counts = Counter.objects.select_related(
        "user").filter(
            room=room_info).annotate(
                raw_timesince=ExpressionWrapper(
                    (timezone.now() - F('created_at')), output_field=fields.DurationField())).order_by('-raw_timesince')[:10]
    
    counting = Counter.objects.filter(user=request.user, room=room_info).exists()
    context = {'room': room_info, 'participants': participants, 'counting': counting, 'room_counts': enumerate(room_counts, 1)}
    return render(request, 'base/room.html', context)
# optimize the n + 1 problem every where

class UpdateRoom(LoginRequiredMixin, View): 
    login_url ='/login/'
    def get(self, request,  pk, *args, **kwargs): 
        room = Room.objects.select_related('genre').get(pk=pk)
        UpdateRoom = CreateRoomForm(instance=room)
        genres = Genre.objects.all()
        context = {'update_form': UpdateRoom, 'genres': genres, 'room': room}
        return render(request, 'base/update_room.html', context)   
    def post(self, request, pk, *args, **kwargs): 
        room = Room.objects.select_related('genre').get(pk=pk)
        post_data = request.POST.copy()

        genre_name = post_data.get('genre_name')
        if genre_name: 
            genre, created = Genre.objects.get_or_create(name=genre_name)
            post_data['genre'] = genre
        
        UpdateForm = CreateRoomForm(post_data, instance=room)
        if UpdateForm.is_valid(): 
            form = UpdateForm.save(commit=False)
            if form.password: 
                room.private = True
            else:
                room.private = False
            form.save()

            messages.success(request, "Room sucessfully updated!")
            return redirect('room', pk=pk)
        genres = Genre.objects.all()
        context = {'update_form': UpdateForm, 'genres': genres, 'room': room}
        return render(request, 'base/update_room.html', context) 
    
def DeleteRoom(request, pk):
    room = Room.objects.get(pk=pk)
    room_name = room.room_name
    room.delete()
    messages.success(request, f"{room_name} room has been deleted" ) 
    return redirect('home')
    

class SearchFriend(View): 
    def get(self, request, *args, **kwargs): 
        search_result = request.GET.get('q')
        if search_result: 
            results = User.objects.filter(username__icontains=search_result)
        else: 
            results = []
        pagination = Paginator(results, 2)
        pagenumber = request.GET.get('page')
        users = pagination.get_page(pagenumber)
        context = {'search_results': enumerate(users, 1), 'results': users, 'query': search_result}
        return render(request, 'base/search_friend.html', context)
    

def friendRequest(request): 
    pending_receiver_requests = PendingRequest.objects.select_related('sender').filter(receiver = request.user)
    requests = []
    for pending_receiver_request in pending_receiver_requests: 
        requests.append(pending_receiver_request.sender)
    context = {'pending_requests': enumerate(requests, start=1)}
    return render(request, 'base/friend_request.html', context)

def createFriendRequest(request, pk): 
    sender = request.user
    receiver = User.objects.get(pk=pk)
    PendingRequest.objects.create(
        sender = sender, 
        receiver = receiver
    )
    messages.success(request, "Friend Request Sent! ")
    return redirect('profile', pk=pk)
    
def addFriend(request, pk): 
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
    messages.success(request, 'Sucessfully added a Friend! ')
    return redirect('friend_request')

def friendRequestRejected(request, pk): 
    Sender = User.objects.get(pk = pk)
    pending_row = Sender.friendRequestFrom.get(receiver=request.user)
    pending_row.delete()
    messages.success(request, 'Request Deleted!')
    return redirect('friend_request')


def displayFriendList(request): 
    Friends = Friend.objects.select_related('friend2').filter(friend1 = request.user)
    friendList = []
    for friendRow in Friends: 
        friendList.append(friendRow.friend2)
    context = {'friendList': friendList}
    return render(request, 'base/friend_list.html', context)


def startCounter(request, pk): 
    Counter.objects.create(
        user = request.user, 
        room = Room.objects.get(pk=pk)
    )
    messages.success(request, "You have started the counter ")
    return redirect('room', pk=pk)

def stopCounter(request, pk): 
    count_object = Counter.objects.filter(user=request.user, room=Room.objects.get(pk=pk))
    count_object.delete()
    messages.success(request, "You have stopped the counter ")
    return redirect('room', pk=pk)

def leaderboard(request, pk): 
    room = Room.objects.get(pk=pk)
    room_counts = Counter.objects.select_related(
        "user").filter(
            room=room).annotate(
                raw_timesince=ExpressionWrapper(
                    (timezone.now() - F('created_at')), output_field=fields.DurationField())).order_by('-raw_timesince')
    context = {'room_counts': enumerate(room_counts), 'room': room}
    return render(request, 'base/leaderboard.html', context)

class RoomAuthorization(View): 
    def get(self, request, pk, *args, **kwargs): 
        room = Room.objects.get(pk=pk)
        context = {'room': room}
        return render(request, 'base/room_authorization.html', context)
    def post(self, request, pk, * args, **kwargs): 
        room_form = RoomAuthorizationForm(request.POST)
        room = Room.objects.get(pk=pk)
        if room_form.is_valid(): 
            password = room_form.cleaned_data['password']
            room_password = room.password
            if password == room_password: 
                messages.success(request, "authenticated")
                return redirect("room", pk=pk)
            else: 
                messages.success(request, "try again")
                return redirect("room_authorization", pk=pk)
            
        context = {'room': room}
        return render(request, 'base/room_authorization.html', context)
    
def participants(request, pk): 
    room = Room.objects.get(pk=pk)
    #moderator group creation/fetch
    groupName = f"{room.room_name}_moderators"
    moderators, created = Group.objects.get_or_create(name=groupName)
    isPrivate = room.private
    isUserModerator = moderators.user_set.filter(pk=request.user.pk).exists()
    participants = room.participants.all().annotate(is_moderator=Exists(
        moderators.user_set.filter(pk=OuterRef('pk'))
        #how does it know pk is of the user 
    ))
    context = {'participants': enumerate(participants, 1), 'room': room, 'isPrivate': isPrivate, 'isUserModerator': isUserModerator}
    return render(request, 'base/Participants.html', context)

def addModerator(request, room_pk, user_pk):
    room = Room.objects.get(pk = room_pk)
    candidate = User.objects.get(pk = user_pk)

    groupName = f"{room.room_name}_moderators"
    group = Group.objects.get(name=groupName)
    
    candidate.groups.add(group)
    messages.success(request, "sucessfully promoted! ")
    return redirect('participants', pk=room.pk)

def removeModerator(request, room_pk, user_pk): 
    room = Room.objects.get(pk=room_pk)
    candidate = User.objects.get(pk=user_pk)

    groupName = f"{room.room_name}_moderators"
    group = Group.objects.get(name=groupName)

    candidate.groups.remove(group)
    messages.success(request, "sucessfully demoted!")
    return redirect('participants', pk=room_pk)

def removeParticipant(request, room_pk, user_pk): 
    room = Room.objects.get(pk=room_pk)
    user = User.objects.get(pk=user_pk)

    #if user was a moderator 
    groupName = f"{room.room_name}_moderators"
    group = Group.objects.get(name=groupName)
    if group.user_set.filter(pk=user.pk): 
        group.user_set.remove(user)

    room.participants.remove(user)
    messages.success(request, "sucessfully removed!")
    return redirect('participants', pk=room_pk)


