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
    
class Room(models.Model): 
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room', null=True)
    room_name = models.CharField(max_length=50, unique=True)
    participants = models.ManyToManyField(User, related_name='joined_room')
    description = models.TextField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta: 
        ordering = ['updated', 'created']

class Friend(models.Model): 
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='friendTo')

    class Meta: 
        constraints = [
            UniqueConstraint(fields=['friend1', 'friend2'], name='friends')
        ]

class PendingRequest(models.Model): 
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='friendRequestFrom')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='friendRequestTo')

    class Meta: 
        constraints = [
            UniqueConstraint(fields=['sender', 'receiver'], name='requests')
        ]
    