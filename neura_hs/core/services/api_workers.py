from django.conf import settings
import requests

LOCALE_LIST = ['enUS', 'ruRU']
ENDPOINT_LIST = ['info', 'cards']


class HsApiConnection:

    def __init__(self, endpoint: str, locale: str = 'enUS'):
        self.__headers = {'x-rapidapi-key': settings.X_RAPIDARI_KEY, 'x-rapidapi-host': settings.HSAPI_HOST}
        self.__endpoint = endpoint
        self.__locale = locale
        self.__check_endpoint()
        self.__check_locale()

    def __check_endpoint(self) -> None:
        if self.__endpoint not in ENDPOINT_LIST:
            raise ValueError(f'Endpoint must be one of {ENDPOINT_LIST}')

    def __check_locale(self) -> None:
        if self.__locale not in LOCALE_LIST:
            raise ValueError(f'Locale must be one of {LOCALE_LIST}')

    def get(self):
        """ Выполняет запрос, возвращает данные в JSON """
        url = settings.HSAPI_BASEURL + self.__endpoint.lower()
        r = requests.get(url=url, headers=self.__headers, params={'locale': self.__locale}, stream=True)
        r.raise_for_status()
        return r.json()
