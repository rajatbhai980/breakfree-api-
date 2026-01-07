from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()
class LoginModel(AuthenticationForm): 
    #adding html attributes 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): 
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
class RegisterModel(UserCreationForm): 
    class Meta: 
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): 
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

class EditUser(ModelForm): 
    class Meta: 
        model = User
        fields = ["first_name", "last_name", "email"]

class EditUserProfile(ModelForm):
    class Meta: 
        model = Profile
        fields = ["phone_no", "bio", "profile_pic"]