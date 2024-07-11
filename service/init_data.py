import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
django.setup()

from django.contrib.auth.models import User
from clients.models import Client
from services.models import Service, Plan, Subscription


def create_users_and_clients(num_users):
    for i in range(num_users):
        username = f'user{i + 1}'
        email = f'user{i + 1}@example.com'
        password = 'password123'
        user = User.objects.create_user(username=username, email=email, password=password)
        company_name = f'Client Company {i + 1}'
        Client.objects.create(user=user, company_name=company_name)


def create_services(num_services):
    for i in range(num_services):
        name = f'Service {i + 1}'
        full_price = random.randint(50, 500)
        Service.objects.create(name=name, full_price=full_price)


def create_plans(num_plans):
    plan_types = ['full', 'student', 'discount']
    for i in range(num_plans):
        plan_type = random.choice(plan_types)
        discount_percent = random.randint(0, 50)
        Plan.objects.create(plan_type=plan_type, discount_percent=discount_percent)


def create_subscriptions(num_subscriptions):
    clients = Client.objects.all()
    services = Service.objects.all()
    plans = Plan.objects.all()

    for i in range(num_subscriptions):
        client = random.choice(clients)
        service = random.choice(services)
        plan = random.choice(plans)

        Subscription.objects.create(client=client, service=service, plan=plan)


def create_initial_data(num_users=1000, num_services=50, num_plans=3, num_subscriptions=5000):
    create_users_and_clients(num_users)
    create_services(num_services)
    create_plans(num_plans)
    create_subscriptions(num_subscriptions)

    print('Initial data created successfully.')


if __name__ == '__main__':
    create_initial_data()
