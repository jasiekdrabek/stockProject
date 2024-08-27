from django.db import models

class TradeCpu(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    replica_id = models.IntegerField()
    