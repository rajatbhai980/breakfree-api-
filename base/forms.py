from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()
class LoginModel(AuthenticationForm): 
    #adding html attributes 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): 
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
