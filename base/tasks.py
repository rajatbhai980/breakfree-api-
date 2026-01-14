import datetime
from django.utils import timezone
from celery import shared_task
from .models import PendingRequest

@shared_task
def delete_friend_request(): 
    time_limit = timezone.now - datetime.timedelta(minutes=1)
    expired_objects =  PendingRequest.objects.filter(created_at_lte=time_limit)
    expired_objects.delete()
    