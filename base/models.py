from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    
class room(models.Model): 
    host = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='room', null=True)
    room_name = models.CharField(max_length=50)
    participants = models.ManyToManyField(User, related_name='joined_room')
    description = models.TextField(max_length=500, null=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta: 
        ordering = ['updated', 'created']

    
    