from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .forms import LoginModel
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages 

# Create your views here.
def home(request):
    return render(request, "base/home.html", {})

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

