from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    # image = models.TextField(blank=False, null=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    depth = models.PositiveIntegerField(default=0)
