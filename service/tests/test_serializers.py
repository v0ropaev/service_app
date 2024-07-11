"""
Модуль с тестами сериализаторов приложения services.

Этот модуль содержит юнит-тесты для проверки правильности работы сериализаторов
PlanSerializer и SubscriptionSerializer.

Тесты:
- test_plan_serializer: Проверяет сериализацию объекта Plan в ожидаемый словарь.
- test_subscription_serializer: Проверяет сериализацию объекта Subscription в ожидаемый словарь.
- test_subscription_serializer_validation_error: Проверяет обработку ошибок валидации для SubscriptionSerializer.
"""

from django.db.models import Prefetch
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict

from clients.models import Client
from services.models import Subscription, Plan, Service
from services.serializers import PlanSerializer, SubscriptionSerializer


class SerializerTestCase(TestCase):
    def setUp(self):
        """
        Настройка данных для тестов.

        Создает пользователя, клиента, сервис и план подписки для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.client = Client.objects.create(user=self.user, company_name='Test Company')

        self.service = Service.objects.create(name='Test Service', full_price=0)
        self.plan = Plan.objects.create(plan_type='full', discount_percent=10)

        self.subscription = Subscription.objects.create(client=self.client, service=self.service, plan=self.plan)

    def test_plan_serializer(self):
        """
        Тест для PlanSerializer.

        Проверяет, что PlanSerializer правильно сериализует объект Plan в ожидаемый словарь.
        """
        serializer = PlanSerializer(self.plan)
        expected_data = {
            'id': self.plan.id,
            'plan_type': 'full',
            'discount_percent': 10
        }
        self.assertEqual(serializer.data, expected_data)

    def test_subscription_serializer(self):
        """
        Тест для SubscriptionSerializer.

        Проверяет, что SubscriptionSerializer правильно сериализует объект Subscription в ожидаемый словарь.
        """
        subscriptions = Subscription.objects.all().prefetch_related(
            'plan',
            Prefetch('client',
                     queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')
                     )
        )
        data: ReturnDict = SubscriptionSerializer(subscriptions, many=True).data
        expected_data = [{
            'id': self.subscription.id,
            'plan_id': self.subscription.plan.id,
            'plan': {
                'id': self.plan.id,
                'plan_type': 'full',
                'discount_percent': 10
            },
            'price': 0,
            'last_change_time': self.subscription.last_change_time,
            'client_name': 'Test Company',
            'email': 'testuser@example.com'
        }]
        self.assertEqual(expected_data, data)

    def test_subscription_serializer_validation_error(self):
        """
        Тест для обработки ошибок валидации SubscriptionSerializer.

        Проверяет, что SubscriptionSerializer корректно обрабатывает недопустимые данные и выбрасывает ошибки валидации.
        """
        invalid_data = {
            'plan': None,
            'client_name': 'Non Existent Client',
            'email': 'invalid email',
            'price': -10,
            'last_change_time': 'invalid time'
        }
        serializer = SubscriptionSerializer(data=invalid_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
