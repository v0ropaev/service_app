from rest_framework import serializers

from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Plan.

    Сериализует все поля модели Plan.
    """
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.

    Атрибуты:
        plan (PlanSerializer): Сериализатор для вложенного объекта плана.
        client_name (CharField): Поле для отображения названия компании клиента.
        email (EmailField): Поле для отображения email пользователя клиента.
        price (SerializerMethodField): Поле для отображения цены подписки.
        last_change_time (SerializerMethodField): Поле для отображения времени последнего изменения подписки.

    Методы:
        get_price(instance): Возвращает цену подписки.
        get_last_change_time(instance): Возвращает время последнего изменения подписки.
    """
    plan = PlanSerializer()
    client_name = serializers.CharField(source='client.company_name')
    email = serializers.EmailField(source='client.user.email')
    price = serializers.SerializerMethodField()
    last_change_time = serializers.SerializerMethodField()

    def get_price(self, instance):
        """
        Возвращает цену подписки.

        Args:
            instance (Subscription): Экземпляр подписки.

        Returns:
            int: Цена подписки.
        """
        return instance.price

    def get_last_change_time(self, instance):
        """
        Возвращает время последнего изменения подписки.

        Args:
            instance (Subscription): Экземпляр подписки.

        Returns:
            datetime: Время последнего изменения подписки.
        """
        return instance.last_change_time

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'plan', 'price', 'last_change_time', 'client_name', 'email')
