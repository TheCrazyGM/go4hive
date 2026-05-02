from django.db import models


class HiveCommunity(models.Model):
    identifier = models.CharField(max_length=50, unique=True)  # e.g. hive-123456
    name = models.CharField(max_length=255)  # e.g. PeakD
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.identifier})"

    class Meta:
        verbose_name_plural = "Hive Communities"
