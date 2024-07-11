"""
Конфигурация URL для проекта service.

Список `urlpatterns` маршрутизирует URL-адреса на представления. Дополнительную информацию можно найти здесь:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Примеры:
    Представления на основе функций:
    1. Добавьте импорт: from services.views import SubscriptionView
    2. Добавьте URL в urlpatterns: path('', SubscriptionView.as_view(), name='subscription-list')

    Представления на основе классов:
    1. Добавьте импорт: from other_app.views import Home
    2. Добавьте URL в urlpatterns: path('', Home.as_view(), name='home')

Включение другого URL-конфигура:
    1. Импортируйте функцию include(): from django.urls import include, path
    2. Добавьте URL в urlpatterns: path('blog/', include('blog.urls'))

API точки доступа:
    - `/admin/`: Административный интерфейс Django.
    - `/api/subscriptions/`: Конечная точка RESTful API для управления подписками.

"""

from django.contrib import admin
from django.urls import path
from rest_framework import routers

from services.views import SubscriptionView

urlpatterns = [
    path('admin/', admin.site.urls),
]

router = routers.DefaultRouter()
router.register(r'api/subscriptions', SubscriptionView)

urlpatterns += router.urls
