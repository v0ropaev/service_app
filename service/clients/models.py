"""
Модуль с описанием моделей приложения clients.

Этот модуль содержит определение модели Client, представляющей клиента с указанием его компании.

Модели:
- Client: Модель представляет клиента с полями user (связь с моделью User), company_name и company_full_address.

Методы:
- __str__: Возвращает строковое представление объекта клиента в формате "Client <id> | <название компании>".
"""

from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    company_full_address = models.CharField(max_length=100)

    def __str__(self):
        """
        Возвращает строковое представление объекта клиента.

        Формат: "Client <id> | <название компании>"
        """
        return f'Client {self.pk} | {self.company_name}'
