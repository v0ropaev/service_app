from rest_framework import serializers

from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    client_name = serializers.CharField(source='client.company_name')
    email = serializers.EmailField(source='client.user.email')
    price = serializers.SerializerMethodField()
    last_change_time = serializers.SerializerMethodField()

    def get_price(self, instance):
        return instance.price

    def get_last_change_time(self, instance):
        return instance.last_change_time

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'plan', 'price', 'last_change_time', 'client_name', 'email')
