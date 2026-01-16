from django.urls import path
from . import views 
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.Register.as_view(), name='register'),
    path('profile/<int:pk>/', views.Profile.as_view(), name='profile'),
    path('edit_profile/<int:pk>/', views.EditProfile.as_view(), name='edit_profile'),
    path('create_room/', views.CreateRoom.as_view(), name='create_room'), 
    path('room/<int:pk>/', views.room, name='room'),
    path('search_friend/', views.SearchFriend.as_view(), name='search_friend'), 
    path('friend_requests/', views.friendRequest, name='friend_request'), 
    path('friend_request_rejected/<int:pk>/', views.friendRequestRejected, name='friend_request_rejected'), 
    path('add_friend/<int:pk>/', views.addFriend, name='add_friend'),
    path('send_friend_request/<int:pk>/', views.createFriendRequest, name='send_request'), 
    path('friend_list/', views.displayFriendList, name='friend_list'), 
    path('start_counter/<int:pk>/', views.startCounter, name='start_counter'),
    path('stop_counter/<int:pk>/', views.stopCounter, name='stop_counter'),
]