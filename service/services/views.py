from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch, F, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    """
    Представление только для чтения, отображающее подписки клиентов с предвыборкой связанных данных.

    Атрибуты:
        queryset (QuerySet): Запрос для выборки всех подписок с предвыборкой связанных планов и клиентов.
        serializer_class (Serializer): Класс сериалайзера для подписок.

    Методы:
        list(request, *args, **kwargs): Переопределенный метод для обработки GET-запросов,
                                        возвращающий список подписок с общей суммой цен.
    """
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client',
                 queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')
                 )
    )
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запросы, возвращая список подписок с общей суммой цен.

        Если общая сумма цен подписок есть в кэше, она используется. Иначе
        она вычисляется и сохраняется в кэш на час.

        Args:
            request (Request): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с данными подписок и общей суммой цен.
        """
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.PRICE_CACHE_NAME)

        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60 * 60)

        response_data = {
            'result': response.data,
            'total_amount': total_price
        }
        response.data = response_data

        return response
