from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model): 
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')   
    bio = models.TextField(blank=True, max_length=500)
    phone_no = models.TextField(blank=True, max_length=10)
    profile_pic = models.ImageField(upload_to="pp/", null = True, blank = True, default='pp/default.jpg')