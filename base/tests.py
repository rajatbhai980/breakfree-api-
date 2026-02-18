from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Room, Genre
from rest_framework import status 
from django.urls import reverse 
from .serializers import RoomSerializer
import json 
# Create your tests here.

class TestHome(APITestCase): 
    def setUp(self): 
        self.user = User.objects.create_user(username="rajat", password='123')
        self.client.force_login(self.user)

    def test_filtering(self): 
        url = reverse("home")
        test_genre = Genre.objects.create(name="test_genre")
        Room.objects.create(room_name="test_room", host=self.user, genre=test_genre)

        response = self.client.get(url, format='json', data={'genre': 'test_genre'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['rooms']), 1)
        self.assertEqual(response.data['rooms'][0]['room_name'], 'test_room')

    def test_pagination(self): 
        url = reverse('home')
        Room.objects.create(room_name="test_1", host=self.user)
        Room.objects.create(room_name="test_2", host=self.user)
        Room.objects.create(room_name="test_3", host=self.user)
        Room.objects.create(room_name="test_4", host=self.user)
        Room.objects.create(room_name="test_5", host=self.user)
        
        response = self.client.get(url, format='json', data={'page': 2})
        self.assertEqual(len(response.data['rooms']), 2)
        self.assertEqual(response.data['rooms'][0]['room_name'], 'test_4')
    
    def test_empty_rooms(self): 
        url = reverse('home')
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['rooms'], [])        

    def test_combined_filtering_pagination(self): 
        url = reverse("home")
        test_genre = Genre.objects.create(name="test_genre")
        Room.objects.create(room_name="test_1", host=self.user, genre=test_genre)
        Room.objects.create(room_name="test_2", host=self.user)
        Room.objects.create(room_name="test_3", host=self.user, genre=test_genre)
        Room.objects.create(room_name="test_4", host=self.user)
        Room.objects.create(room_name="test_5", host=self.user, genre=test_genre)
        Room.objects.create(room_name="test_6", host=self.user)
        Room.objects.create(room_name="test_7", host=self.user, genre=test_genre)

        response = self.client.get(url, format='json', data={'genre': 'test_genre', 'page': 2})
        self.assertEqual(response.data['rooms'][0]['room_name'], 'test_7')
    #continue testing  