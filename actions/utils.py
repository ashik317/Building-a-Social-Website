from django.contrib.contenttypes.models import ContentType
import datetime
from .models import Action
from django.utils import timezone

def create_action(user, verb, target=None):
    actions = Action(user=user, verb=verb, target=target)
    actions.save()

    now = timezone.now()
    last_minute = now - datetime.timedelta(minutes=1)
    similar_actions = Action.objects.filter(user_id = user.id, verb=verb, created__gte=last_minute)

    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_id=target.id, target_ct=target_ct)

    if not similar_actions:
        actions = Action(user=user, verb=verb, target=target)
        actions.save()
        return True
    return False
