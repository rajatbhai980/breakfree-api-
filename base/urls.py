from django.urls import path, include
from . import views 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'view_all_genre', views.ViewAllGenre, basename='view_all_genre')
router.register(r'room_viewset', views.RoomViewSet, basename="room_viewset")


urlpatterns = [
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
    path('room/<int:pk>/', views.room, name='room'),
    path('', include(router.urls)),
    path('create_friend_request/<int:pk>/', views.create_friend_request, name='create_friend_request'),
    path('view_friend_requests/', views.view_friend_request, name='view_friend_requests'),
    path('accept_friend_request/<int:pk>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:pk>/', views.reject_friend_request, name='reject_friend_request'), 
    path('remove_friend/<int:pk>/', views.remove_friend, name='remove_friend'),
    path('friend_list/', views.view_friend_list, name='friend_list'),
    path('search_friend/', views.SearchFriend.as_view(), name='search_friend'), 
]