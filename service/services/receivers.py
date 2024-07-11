"""
Модуль для обработчиков сигналов Django.

Этот модуль содержит обработчики сигналов для выполнения действий в ответ на определенные события.

Функции:
- delete_cache_total_sum: Обработчик сигнала post_delete для удаления кэша суммарной стоимости.
"""

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=None)
def delete_cache_total_sum(*args, **kwargs):
    """
    Обработчик сигнала post_delete для удаления кэша суммарной стоимости.

    Args:
        *args: Позиционные аргументы.
        **kwargs: Ключевые аргументы.

    Использует настройку settings.PRICE_CACHE_NAME для удаления кэша.
    """
    cache.delete(settings.PRICE_CACHE_NAME)
