from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Image
from django.db.models import Count

@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_changed(sender, instance, **kwargs):
 instance.total_likes = instance.users_like.count()
 instance.save()
 images_by_popularity = Image.objects.annotate(likes=Count('users_like')).order_by('-likes')