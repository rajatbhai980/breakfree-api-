from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import Profile, Room

User = get_user_model()


class EditUser(ModelForm): 
    class Meta: 
        model = User
        fields = ["first_name", "last_name", "email"]

class EditUserProfile(ModelForm):
    class Meta: 
        model = Profile
        fields = ["phone_no", "bio", "profile_pic"]

class CreateRoomForm(ModelForm): 
    class Meta: 
        model = Room
        fields = ["room_name", "description", 'password', 'genre']
        error_messages = {
            'room_name':{
                'unique': ('The room with that name already exists!!')
            },
            
        }

class RoomAuthorizationForm(ModelForm): 
    class Meta: 
        model = Room 
        fields = ["password"]


    