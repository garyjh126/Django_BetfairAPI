# from django.contrib.auth.models import User
from .models import Runner
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Runner)
def announce_new_runner(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "gossip", {"type": "runner.gossip",
                       "event": "New Runner",
                       "runnerId": instance.selectionId})