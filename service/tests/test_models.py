"""
Модуль с тестами моделей приложения services.

Этот модуль содержит юнит-тесты для моделей Service, Plan и Subscription.

Тесты:
- ServiceModelTestCase: Тесты для модели Service, проверяющие поведение метода save().
- PlanModelTestCase: Тесты для модели Plan, проверяющие поведение метода save() и валидацию максимальной скидки.
- SubscriptionModelTestCase: Тесты для модели Subscription, проверяющие поведение метода save().

"""

from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch
from django.core.exceptions import ValidationError
from clients.models import Client
from services.models import Service, Plan, Subscription


class ServiceModelTestCase(TestCase):
    """
    Тесты для модели Service.
    """

    def setUp(self):
        """
        Подготовка данных для тестирования.
        """
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.client = Client.objects.create(user=self.user, company_name='Test Company')
        self.service = Service.objects.create(name='Test Service', full_price=100)
        self.plan = Plan.objects.create(plan_type='full', discount_percent=10)
        self.subscription = Subscription.objects.create(client=self.client, service=self.service, plan=self.plan)

    def test_service_save_method_with_price_update_task(self):
        """
        Тестирование метода save() модели Service с обновлением цены.
        """
        with patch('services.tasks.set_price.delay') as mock_set_price_delay:
            self.service.full_price = 150
            self.service.save()
            for subscription in self.service.subscriptions.all():
                mock_set_price_delay.assert_called_once_with(subscription.id)

    def test_service_save_method_without_price_update_task(self):
        """
        Тестирование метода save() модели Service без обновления цены.
        """
        with patch('services.tasks.set_price.delay') as mock_set_price_delay:
            self.service.name = 'Updated Service Name'
            self.service.save()
            mock_set_price_delay.assert_not_called()

    def test_service_save_method_with_last_change_time_task(self):
        """
        Тестирование метода save() модели Service с обновлением времени последнего изменения.
        """
        with patch('services.tasks.set_last_change_time.delay') as mock_set_last_change_time_delay:
            self.service.full_price = 150
            self.service.save()
            for subscription in self.service.subscriptions.all():
                mock_set_last_change_time_delay.assert_called_once_with(subscription.id)

    def test_service_save_method_without_last_change_time_task(self):
        """
        Тестирование метода save() модели Service без обновления времени последнего изменения.
        """
        with patch('services.tasks.set_last_change_time.delay') as mock_set_last_change_time_delay:
            self.service.name = 'Updated Service Name'
            self.service.save()
            mock_set_last_change_time_delay.assert_not_called()


class PlanModelTestCase(TestCase):
    """
    Тесты для модели Plan.
    """

    def setUp(self):
        """
        Подготовка данных для тестирования.
        """
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.client = Client.objects.create(user=self.user, company_name='Test Company')
        self.service = Service.objects.create(name='Test Service', full_price=100)
        self.plan = Plan.objects.create(plan_type='full', discount_percent=10)
        self.subscription = Subscription.objects.create(client=self.client, service=self.service, plan=self.plan)

    def test_plan_save_method_with_price_update_task(self):
        """
        Тестирование метода save() модели Plan с обновлением цены.
        """
        with patch('services.tasks.set_price.delay') as mock_set_price_delay:
            self.plan.discount_percent = 20
            self.plan.save()
            for subscription in self.plan.subscriptions.all():
                mock_set_price_delay.assert_called_once_with(subscription.id)

    def test_plan_save_method_without_price_update_task(self):
        """
        Тестирование метода save() модели Plan без обновления цены.
        """
        with patch('services.tasks.set_price.delay') as mock_set_price_delay:
            self.plan.plan_type = 'student'
            self.plan.save()
            mock_set_price_delay.assert_not_called()

    def test_plan_save_method_with_last_change_time_task(self):
        """
        Тестирование метода save() модели Plan с обновлением времени последнего изменения.
        """
        with patch('services.tasks.set_last_change_time.delay') as mock_set_last_change_time_delay:
            self.plan.discount_percent = 20
            self.plan.save()
            for subscription in self.plan.subscriptions.all():
                mock_set_last_change_time_delay.assert_called_once_with(subscription.id)

    def test_plan_save_method_without_last_change_time_task(self):
        """
        Тестирование метода save() модели Plan без обновления времени последнего изменения.
        """
        with patch('services.tasks.set_last_change_time.delay') as mock_set_last_change_time_delay:
            self.plan.plan_type = 'student'
            self.plan.save()
            mock_set_last_change_time_delay.assert_not_called()

    def test_plan_max_discount_validation(self):
        """
        Тестирование валидации максимальной скидки модели Plan.
        """
        with self.assertRaises(ValidationError):
            plan = Plan(plan_type='discount', discount_percent=101)
            plan.full_clean()


class SubscriptionModelTestCase(TestCase):
    """
    Тесты для модели Subscription.
    """

    def setUp(self):
        """
        Подготовка данных для тестирования.
        """
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.client = Client.objects.create(user=self.user, company_name='Test Company')
        self.service = Service.objects.create(name='Test Service', full_price=100)
        self.plan = Plan.objects.create(plan_type='full', discount_percent=10)
        self.subscription = Subscription.objects.create(client=self.client, service=self.service, plan=self.plan)

    def test_subscription_save_method_with_price_update_task(self):
        """
        Тестирование метода save() модели Subscription с обновлением цены.
        """
        with patch('services.tasks.set_price.delay') as mock_set_price_delay:
            self.subscription.service.full_price = 50
            self.subscription.service.save()
            self.subscription.save()
            mock_set_price_delay.assert_called_with(self.subscription.id)

    def test_subscription_save_method_without_price_update_task(self):
        """
        Тестирование метода save() модели Subscription без обновления цены.
        """
        with patch('services.tasks.set_price.delay') as mock_set_price_delay:
            self.subscription.client.company_name = 'Updated Company'
            self.subscription.client.save()
            self.subscription.save()
            mock_set_price_delay.assert_not_called()
