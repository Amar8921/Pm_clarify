from django.db import models

class DocumentDefinition(models.Model):
    name = models.CharField(max_length=50, unique=True)
    details = models.JSONField()