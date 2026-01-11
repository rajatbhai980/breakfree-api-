from django.urls import path
from . import views 
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.Register.as_view(), name='register'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('edit_profile/<int:pk>/', views.EditProfile.as_view(), name='edit_profile'),
    path('create_room/', views.CreateRoom.as_view(), name='create_room'), 
    path('room/<int:pk>/', views.room, name='room'),
    path('search_friend/', views.SearchFriend.as_view(), name='search_friend')
]