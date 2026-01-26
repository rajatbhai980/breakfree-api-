from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import UniqueConstraint
# Create your models here.
class Profile(models.Model): 
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')   
    bio = models.TextField(blank=True, max_length=500)
    phone_no = models.TextField(blank=True, max_length=10)
    profile_pic = models.ImageField(upload_to="pp/", null = True, blank = True, default='pp/default.jpg')

#signal use? creates profile for the user when it gets created 
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs): 
    if created: 
        Profile.objects.create(user=instance)

class Genre(models.Model): 
    name = models.CharField(unique=True)

    def __str__(self): 
        return str(self.name)

class Room(models.Model): 
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room', null=True)
    room_name = models.CharField(max_length=50, unique=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genre_room', null = True)
    participants = models.ManyToManyField(User, related_name='joined_room')
    description = models.TextField(max_length=500, null=True, blank=True)
    password = models.CharField(max_length=50, blank=True, null=True, default='')
    private = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta: 
        ordering = ['created', 'updated']

    def __str__(self): 
        return self.room_name

class Friend(models.Model): 
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='friendModel')
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta: 
        constraints = [
            UniqueConstraint(fields=['friend1', 'friend2'], name='friends')
        ]

class PendingRequest(models.Model): 
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='friendRequestFrom')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='friendRequestTo')
    created_at = models.DateTimeField(auto_now=True)

    class Meta: 
        constraints = [
            UniqueConstraint(fields=['sender', 'receiver'], name='requests')
        ]
    
class Counter(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_counter')
    created_at = models.DateTimeField(auto_now=True)

    class Meta: 
        constraints = [
            UniqueConstraint(fields=['user', 'room'], name='counts')
        ]
