from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.


def get_release_file_name(instance, filename):
    return f"HearthstoneAccess-{instance.hearthstone_version}-{instance.accessibility_version}.zip"


class Release(models.Model):
    class Meta:
        get_latest_by = "accessibility_version"

    hearthstone_version = models.CharField(max_length=100)
    accessibility_version = models.IntegerField(primary_key=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    changelog = models.TextField(blank=True)
    file = models.FileField(upload_to=get_release_file_name)


class ReleaseChannel(models.Model):
    name = models.SlugField(unique=True)
    description = models.TextField()
    releases = models.ManyToManyField(Release)

    def get_latest_release(self) -> Release:
        try:
            return self.releases.latest()
        except Release.DoesNotExist:
            return None


@receiver(post_delete, sender=Release)
def cleanup_file(sender, instance, **kwargs):
    instance.file.delete(False)
