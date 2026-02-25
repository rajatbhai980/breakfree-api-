from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import Profile, Room

User = get_user_model()

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


    