Сайт микроблогов
=====

[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Unittest](https://img.shields.io/badge/Unittest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)
[![SQLite3](https://img.shields.io/badge/-SQLite3-464646?style=flat-square&logo=SQLite)](https://www.sqlite.org/)

## Описание:

Сайт для ведения публичных микроблогов. У пользователей  есть возможность зарегистрироваться и создавать страницу, писать и редактировать свои записи. Так же у них есть возможность подписываться на  других авторов и оставлять комментарии. Незарегистрированные пользователи могут только просматривать записи авторов и комментарии к ним.

### Функционал:
- Регистрация по электронной почте.
- Создание постов с изображениями.
- Редактирование своих постов.
- Привязка постов к группап по категориям.
- Возможность подписки на других пользователей.
- Комментарии к записям других авторов.
- Лента с записями, на которых оформлена подписка.
- Для владельца ресурса настроена админ-панель с возможностью можерации постов и создания новых групп.

Для проекта написаны тесты Unittest.

## Как запустить проект?:

1. Клонируйте репозиторий с помощью команды __git clone__

2. Создайте виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
3. Установите зависимости:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
4. Выполните миграции на уровне проекта и соберите статику:
```
python3 manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```
5. Создайте суперпользователя Django для работы с админ-панелью:
```
python manage.py createsuperuser

# адрес панели администратора после запуска проекта будет по адресу:
http://127.0.0.1:8000/admin
```
6. Запустите проект локально:
```
python manage.py runserver
```