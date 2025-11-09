from django.db import models

# Create your models here.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimestampedModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    image = models.TextField(blank=False, null=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    depth = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = self.parent.depth + 1
        elif not self.parent:
            self.depth = 0
        super().save(*args, **kwargs)
