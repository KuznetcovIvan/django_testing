from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
import pytest

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """
    Фикстура для создания пользователя
    с именем 'Автор'.
    """
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """
    Фикстура для создания пользователя
    с именем 'Читатель'.
    """
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """
    Фикстура для создания клиента,
    авторизованного как 'Автор'.
    """
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """
    Фикстура для создания клиента,
    авторизованного как 'Читатель'.
    """
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """
    Фикстура для
    создания новости.
    """
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def news_collection():
    """
    Фикстура для создания
    коллекции новостей.
    """
    today = datetime.today()
    return News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Текст',
             date=today - timedelta(days=index)
             ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(author, news):
    """
    Фикстура для
    создания комментария.
    """
    comment = Comment.objects.create(news=news,
                                     author=author,
                                     text='Текст')
    return comment


@pytest.fixture
def comments_collection(news, author):
    """
    Фикстура для создания
    коллекции коментариев.
    """
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(news=news,
                                         author=author,
                                         text=f'Текст {index}')
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.filter(news=news)


@pytest.fixture
def id_for_args(news):
    """
    Фикстура для получения id
    созданной новости в виде кортежа.
    """
    return (news.id,)


@pytest.fixture
def form_data():
    """
    Фикстура возвращающая словарь с данными
    для создания объекта Comment.
    (Значения в этом словаре отличаются от значений
    полей объекта фикстуры comment)
    """
    return {'text': 'Новый текст'}


@pytest.fixture
def bad_words_data():
    """
    Фикстура возвращающая словарь с данными
    для создания объекта Comment, где поле 'text'
    содержит не допустимые слова.
    """
    return {'text': f'Текст со словом - {BAD_WORDS[0]}.'}
