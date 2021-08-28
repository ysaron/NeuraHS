import functools
import traceback
from django.db import transaction
from django.views import View
import logging

logger = logging.getLogger('django')


def log_all_exceptions(func):
    """
    Декоратор для FBV, логирующий необработанные исключения
    :param func: Function-Based View
    """
    @functools.wraps(func)
    def inner(request, *args, **kwargs):
        try:
            with transaction.atomic():
                return func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f'{traceback.format_exc()}')
            raise e

    return inner


class LogAllExceptions(View):
    """ Миксин для CBV, логирующий необработанные исключения """

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f'{traceback.format_exc()}')
            raise e

        return response
