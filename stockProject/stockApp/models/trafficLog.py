from django.db import models

class TrafficLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    request_id = models.CharField(max_length=255)
    api_time = models.FloatField()
