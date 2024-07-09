from celery import shared_task
from celery_singleton import Singleton
from django.db import transaction
from django.db.models import F
from django.utils import timezone


@shared_task(base=Singleton)
def set_price(subscription_id):
    from services.models import Subscription

    with transaction.atomic():
        subscription = Subscription.objects.filter(id=subscription_id).annotate(
            annotated_price=F('service__full_price') - F('service__full_price') * F('plan__discount_percent') / 100.00)
        subscription = subscription.first()

        subscription.price = subscription.annotated_price
        subscription.save()


@shared_task(base=Singleton)
def set_last_change_time(subscription_id):
    from services.models import Subscription

    with transaction.atomic():
        subscription = Subscription.objects.get(id=subscription_id)

        subscription.last_change_time = timezone.now()
        subscription.save()
