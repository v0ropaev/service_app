from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    company_full_address = models.CharField(max_length=100)

    def __str__(self):
        return f'Client {self.pk} | {self.company_name}'
