from django.db import models

class MarketLog(models.Model):
    class ApiMethod(models.TextChoices):
        GET = 'GET', 'GET'
        POST = 'POST', 'POST'
        PUT = 'PUT', 'PUT'
        DELETE = 'DELETE', 'DELETE'

    timestamp = models.DateTimeField(auto_now_add=True)
    api_method = models.CharField(max_length=10, choices=ApiMethod.choices)
    application_time = models.FloatField()
    database_time = models.FloatField()
    endpoint_url = models.URLField()
    request_id = models.CharField(max_length=255)

