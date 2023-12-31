from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Image

@receiver(m2m_changed,sender=Image.users_likes.through)
def user_like_change(sender, instance, **kwargs):
    instance.total_likes = instance.users_likes.count()
    instance.save()