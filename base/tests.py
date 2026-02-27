from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Room, Genre, Friend, PendingRequest
from rest_framework import status 
from django.urls import reverse 
from .serializers import RoomSerializer
from rest_framework_simplejwt.tokens import AccessToken
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
    def test_unauthorizedacess(self): 
        self.client.logout()
        url = reverse('home')
        response = self.client.get(url, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    #continue testing  

class TestRegister(APITestCase): 
    def test_sucessful_registration(self): 
        url = reverse('register')
        data = {
            "username": "sheetal", 
            "email": "xetrikto@gmail.com", 
            "password": "classicrider", 
            "password2": "classicrider"
        }
        response = self.client.post(url, format='json', data=data)
        created = User.objects.filter(username="sheetal").exists()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(created)
        
    def test_password_dont_match(self): 
        url = reverse('register')
        data = {
            "username": "kapil", 
            "email": "xetrikto@gmail.com", 
            "password": "classicrider", 
            "password2": "classicrides"
        }
        response = self.client.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email(self): 
        url = reverse('register')
        data = {
            "username": "oggy", 
            "email": "", 
            "password": "classicrider", 
            "password2": "classicrider"
        }
        response = self.client.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dublicate_user(self): 
        url = reverse('register')
        data1 = {
            "username": "pranjal", 
            "email": "din@gmail.com", 
            "password": "classicrider", 
            "password2": "classicrider"
        }
        data2 = {
            "username": "pranjal", 
            "email": "din@gmail.com", 
            "password": "classicsinger", 
            "password2": "classicsinger"
        }
        response = self.client.post(url, format='json', data=data1)
        response2 = self.client.post(url, format='json', data=data2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

class TestLogin(APITestCase): 
    def setUp(self): 
        self.user = User.objects.create_user(username="pranjal", password="singer")
        self.url = reverse('login')
    def test_sucessful_login(self): 
        data = {
            "username": "pranjal", 
            "password": "singer", 
        }
        response = self.client.post(self.url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_wrong_password(self): 
        data = {
            "username": "pranjal", 
            "password": "wrong_pass", 
        }
        response = self.client.post(self.url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_username(self): 
        data = {
            "password": "singer", 
        }
        response = self.client.post(self.url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_structure(self): 
        data = {
            "username": "pranjal", 
            "password": "singer", 
        }
        response = self.client.post(self.url, format='json', data=data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

        token_obj = AccessToken(response.data['access_token'])
        self.assertEqual(self.user.id, int(token_obj['user_id']))

class TestProfile(APITestCase):
    def setUp(self): 
        self.user1 = User.objects.create_user(username="rajat", password="freefire")
        self.user2 = User.objects.create_user(username="pranjal", password = "freefire")
        self.client.force_login(self.user1)
    
    def test_non_existing_user_404(self): 
        url = reverse('profile', kwargs={'pk': 10})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
    
    def test_is_friend(self): 
        new_friend = User.objects.create_user(username="micheal", password="why?")
        url=reverse('profile', kwargs={'pk': new_friend.pk})
        Friend.objects.create(friend1=self.user1, friend2=new_friend)
        Friend.objects.create(friend1=new_friend, friend2=self.user1)
        response = self.client.get(url, format='json')
        self.assertTrue(response.data['is_friend'])

    def test_friend_count(self): 
        url = reverse('profile', kwargs={'pk': self.user2.pk})
        response = self.client.get(url , format='json')
        self.assertEqual(response.data['friend_count'], 0)
        Friend.objects.create(friend1=self.user1, friend2=self.user2)
        Friend.objects.create(friend1=self.user2, friend2=self.user1)
        response = self.client.get(url , format='json')
        self.assertEqual(response.data['friend_count'], 1)

    def test_pending_request(self): 
        test_user = User.objects.create_user(username="sheetal", password="bullatrider")
        url = reverse('profile', kwargs={'pk': test_user.pk})
        PendingRequest.objects.create(sender=self.user1, receiver=test_user)
        response = self.client.get(url , format='json')
        self.assertTrue(response.data['pending'])

class TestEditProfile(APITestCase): 
    def setUp(self):
        self.user = User.objects.create_user(username="rajat", password='freefire')
        self.url = reverse('edit_profile')
        self.client.force_login(self.user)
    
    def test_sucessful_200(self): 
        data = {
            "user": {
                "username": "evolved_rajat", 
                "email": "gamerbhai@gmail.com"
            }, "profile": {
                "bio": "anime watching machine"
            }
        }
        profile_url = reverse('profile', kwargs={'pk': self.user.pk})
        edit_response = self.client.patch(self.url, format='json', data=data)
        profile_page_response = self.client.get(profile_url, format='json')
        self.assertEqual(edit_response.status_code, status.HTTP_200_OK)
        print(profile_page_response.data)
        self.assertEqual(profile_page_response.data['user']['username'], "evolved_rajat")
        self.assertEqual(profile_page_response.data['profile']['bio'], "anime watching machine")
    
    def test_empty_body_200(self):
        edit_response = self.client.patch(self.url, format='json')
        self.assertEqual(status.HTTP_200_OK, edit_response.status_code)
    
    def test_dublicate_username_400(self): 
        User.objects.create_user(username="tennisplayer", password="123")
        data = {
            "user":{
                "username": "tennisplayer"
            }
        }
        edit_response = self.client.patch(self.url, format='json', data=data)
        self.assertEqual(edit_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_related_info_200(self): 
        edit_response = self.client.get(self.url, format='json')
        self.assertEqual(edit_response.status_code, status.HTTP_200_OK)
        self.assertEqual(edit_response.data['user']['username'], self.user.username)

    def test_unauthenticated_acess_401(self): 
        self.client.logout()
        edit_response = self.client.patch(self.url, format='json')
        self.assertEqual(edit_response.status_code, status.HTTP_401_UNAUTHORIZED)

#test ideas for create room 
class TestCreateRoom(APITestCase): 
    def setUp(self): 
        self.user = User.objects.create_user(username="rajat", password="123456")
        self.client.force_login(self.user)
        self.url = reverse('create_room')
        self.data = {
    "room_name": "Football", 
    "genre_name": "sports", 
    "description": "test",  
    "password": "123"
        }       
    def test_sucessful_creation_201(self): 
        response = self.client.post(self.url, format='json', data=self.data)
        room = Room.objects.get(room_name='Football')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('Football', room.room_name)
        self.assertEqual('sports', room.genre.name)
        self.assertEqual('123', room.password)
        participants = room.participants.all()
        self.assertIn(self.user, participants)
    
    def test_dublicate_room_creation_400(self): 
        Room.objects.create(room_name="Football")
        response = self.client.post(self.url, format='json', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_empty_room_name(self): 
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)