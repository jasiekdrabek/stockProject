from django.db import models

class Cpu(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    contener_id = models.CharField()