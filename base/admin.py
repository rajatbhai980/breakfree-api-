from django.contrib import admin
from .models import Profile, Room, Friend, PendingRequest, Counter, Genre
# Register your models here.
admin.site.register(Profile)
admin.site.register(Room)
admin.site.register(Friend)
admin.site.register(PendingRequest)
admin.site.register(Counter)
admin.site.register(Genre)