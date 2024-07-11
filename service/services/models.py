from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.utils import timezone

from clients.models import Client
from .receivers import delete_cache_total_sum
from .tasks import set_price, set_last_change_time


class Service(models.Model):
    """
    Модель, представляющая услугу.

    Attributes:
        name (str): Название услуги.
        full_price (int): Полная цена услуги.

    Methods:
        save(*args, **kwargs): Переопределенный метод сохранения, который запускает
                               асинхронные задачи для обновления подписок.
    """

    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f'Service {self.pk} | {self.name}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):
        """
        Переопределенный метод сохранения для запуска асинхронных задач при изменении цены услуги.
        """
        if self.__full_price != self.full_price and self.pk is not None:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_last_change_time.delay(subscription.id)

        return super().save(*args, **kwargs)


class Plan(models.Model):
    """
    Модель, представляющая план подписки.

    Attributes:
        PLAN_TYPES (tuple): Кортеж с вариантами типов плана.
        plan_type (str): Тип плана (например, 'full', 'student', 'discount').
        discount_percent (int): Процент скидки для плана.

    Methods:
        save(*args, **kwargs): Переопределенный метод сохранения, который запускает
                               асинхронные задачи для обновления подписок.
    """

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
        """
        Переопределенный метод сохранения для запуска асинхронных задач при изменении скидки плана.
        """
        if self.__discount_percent != self.discount_percent and self.pk is not None:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_last_change_time.delay(subscription.id)

        return super().save(*args, **kwargs)


class Subscription(models.Model):
    """
    Модель, представляющая подписку клиента на услугу.

    Attributes:
        client (Client): Внешний ключ на модель клиента.
        service (Service): Внешний ключ на модель услуги.
        plan (Plan): Внешний ключ на модель плана подписки.
        price (int): Цена подписки.
        last_change_time (datetime): Время последнего изменения подписки.

    Meta:
        indexes (list): Список индексов для ускорения запросов по клиенту и услуге.

    Methods:
        save(*args, **kwargs): Переопределенный метод сохранения, который запускает
                               асинхронные задачи при создании новой подписки.
    """

    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    last_change_time = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['client', 'service']),
        ]

    def __str__(self):
        return f'Subscription {self.pk} | {self.service.name}'

    def save(self, *args, **kwargs):
        """
        Переопределенный метод сохранения для запуска асинхронной задачи при создании подписки.
        """
        creating = not bool(self.id)
        saved_instance = super().save(*args, **kwargs)
        if creating:
            set_price.delay(self.id)
        return saved_instance


post_delete.connect(delete_cache_total_sum, sender=Subscription)
