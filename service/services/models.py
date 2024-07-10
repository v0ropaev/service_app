from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from clients.models import Client
from .tasks import set_price, set_last_change_time


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f'Service {self.pk} | {self.name}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):
        if self.__full_price != self.full_price and self.pk is not None:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_last_change_time.delay(subscription.id)

        return super().save(*args, **kwargs)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        if self.__discount_percent != self.discount_percent and self.pk is not None:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_last_change_time.delay(subscription.id)

        return super().save(*args, **kwargs)


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    last_change_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Subscription {self.pk} | {self.service.name}'
