# NeuraHS

[![Python](https://img.shields.io/badge/python-v3.9.9-blueviolet.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-v3.2.7-blue.svg?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/django--rest--framework-v3.12.4-blue.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/license-MIT-9cf.svg)](https://opensource.org/licenses/MIT)

> http://91.227.18.9/
----
## Описание
Вспомогательный сервис для игроков [Hearthstone](https://playhearthstone.com/).  
Hearthstone - коллекционная карточная игра. Колоды в ней составляются из 30 карт и копируются из клиента игры как байтовые строки в Base64 (для удобства). Основная функция сайта - расшифровка по известному алгоритму и удобный просмотр колод.  

----
### Функционал

- Колоды
  - **Расшифровка кодов колод[^1] и их детализированный просмотр.**  
    Каждая колода содержит ссылки на включенные в нее карты.  
    Также отображаются похожие колоды (при наличии таковых в БД).
  - **Хранилище колод.**  
    Расшифрованные колоды сохраняются и доступны для просмотра (в т.ч. посредством API).
  - Авторизованные пользователи могут сохранять колоды в личном хранилище, доступном только им (клиент игры на данный момент позволяет сохранять только 27 колод одновременно).
- Карты
  - **База данных карт Hearthstone** (в т.ч. неколлекционные карты, недоступные для включения в колоду).  
    *Источник: https://rapidapi.com/omgvamp/api/hearthstone*  
    *Источник изображений: https://hearthstonejson.com*  
    Обновление базы: `python manage.py hs_base_update`
  - **Фан-карты** (карты с произвольными характеристиками): CRUD-операции.  
    - Создание карт доступно авторизованным пользователям. 
    - Карта будет доступна для просмотра после премодерации.
    - Никнеймы пользователей, имеющих прошедшие премодерацию карты, появляются в списке авторов.
    - Изменять/удалять карту может только ее автор и пользователи с особыми правами (редакторы).
- Общедоступный API для read-only доступа к картам и колодам  
  *Фильтрация по названию, классам, типам, форматам; поиск колод по включенным картам; получение карт колоды по коду.*  
  *Документация сгенерирована Swagger.*
- Всякая бесполезная статистика, плод упражнений в Django ORM.

[^1]: В т.ч. того вида, в котором они копируются из клиента игры

---
### Прочее

- I18n & l10n (английский и русский язык).  
  *Переключение языка - на боковой панели.*
- Система аккаунтов
  - Регистрация с подтверждением email.
  - Сброс пароля через email.
  - Авторизация открывает доступ к созданию фан-карт и сохранению колод.
- Логирование ошибок в middleware.
- Юнит-тестирование (pytest).
- Сайт развернут с использованием Nginx, Gunicorn, PostgreSQL.
