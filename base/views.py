from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .forms import LoginModel, RegisterModel, EditUserProfile, EditUser, CreateRoomForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .models import Room 


#for getting the user model 
User = get_user_model()

# Create your views here.
def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, "base/home.html", context)

class Login(View): 
    def get(self, request, *args, **kwargs): 
        login_form = LoginModel()
        context = {'login_form': login_form}
        return render(request, 'base/login.html', context)
        # return render(request, "base/login.html", context)

    def post(self, request, *args, **kwargs): 
        #adding validation 
        form = LoginModel(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            if user is not None: 
                login(request, user)
                messages.success(request, 'You have been logged in')
                return redirect('home')

            form.add_error(None, 'Invalid Username or Password')
        context = {'login_form': form}
        return render(request, "base/login.html", context)

def logout_user(request): 
    logout(request)
    messages.success(request, "You have sucessfully logged out!")
    return redirect('home')

class Register(View): 
    def get(self, request, *args, **kwargs): 
        form = RegisterModel()
        context = {'form': form}
        return render(request, 'base/register.html', context)
    def post(self, request, *args, **kwargs): 
        form = RegisterModel(request.POST)
        if form.is_valid(): 
            form.save()
            #for loggin in right after the register form is accepted 
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            if user is not None: 
                login(request, user)
                messages.success(request, "You have been registered")
                return redirect("home")
        return render(request, "base/register.html", {'form': form})
    

def profile(request, pk):
    user = User.objects.get(pk=pk) 
    context = {'user':user}
    return render(request, 'base/profile.html', context)

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
        room_form = CreateRoomForm(initial={'host': request.user})
        context = {'room_form': room_form}
        return render(request, "base/create_room.html", context)

    def post(self, request, *args, **kwargs):
        room_form = CreateRoomForm(request.POST)
        if room_form.is_valid():
            room = room_form.save(commit=False)
            room.host = request.user
            room.save()
            messages.success(request, "You have created a room. ")
            return redirect("home")
            
        context = {'room_form': room_form}
        return render(request, "base/create_room.html", context)    
    
@login_required
def room(request, pk):
    room_info = Room.objects.get(pk=pk) 
    room_info.participants.add(request.user)
    participants = room_info.participants.all()
    login_url = '/login/'
    context = {'room': room_info, 'participants': participants}
    return render(request, 'base/room.html', context)


class SearchFriend(View): 
    def post(self, request, *args, **kwargs): 
        search_result = request.POST.get('search')
        results = User.objects.filter(username__icontains=search_result)
        context = {'results': results}
        return render(request, 'base/search_friend.html', context)