from django.urls import path, include
from . import views 
from rest_framework import routers


urlpatterns = [
    path('create_room/', views.CreateRoom.as_view(), name='create_room'), 
    path('update_room/<int:pk>/', views.UpdateRoom.as_view(), name='update_room'), 
    path('delete_room/<int:pk>/', views.DeleteRoom, name='delete_room'), 
    path('room/<int:pk>/', views.room, name='room'),
    path('search_friend/', views.SearchFriend.as_view(), name='search_friend'), 
    path('friend_requests/', views.friendRequest, name='friend_request'), 
    path('friend_request_rejected/<int:pk>/', views.friendRequestRejected, name='friend_request_rejected'), 
    path('add_friend/<int:pk>/', views.addFriend, name='add_friend'),
    path('send_friend_request/<int:pk>/', views.createFriendRequest, name='send_request'), 
    path('friend_list/', views.displayFriendList, name='friend_list'), 
    path('start_counter/<int:pk>/', views.startCounter, name='start_counter'),
    path('stop_counter/<int:pk>/', views.stopCounter, name='stop_counter'),
    path('leaderboard/<int:pk>/', views.leaderboard, name='leaderboard'), 
    path('room_authorization/<int:pk>/', views.RoomAuthorization.as_view(), name='room_authorization'),
    path('participants/<int:pk>', views.participants, name='participants'), 
    path('add_moderator/<int:room_pk>/user/<int:user_pk>/', views.addModerator, name='add_moderator'),
    path('remove_moderator/<int:room_pk>/user/<int:user_pk>/', views.removeModerator, name='remove_moderator'), 
    path('remove_participant/<int:room_pk>/user/<int:user_pk>/', views.removeParticipant, name='remove_participant'), 

    #REST API 
    path('', views.home, name='home'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('profile/<int:pk>/', views.ProfilePage.as_view(), name='profile'),
    path('edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    
]