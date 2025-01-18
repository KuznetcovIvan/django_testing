from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_collection():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Текст',
             date=today - timedelta(days=index)
             ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(news=news,
                                  author=author,
                                  text='Текст')


@pytest.fixture
def comments_collection(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(news=news,
                                         author=author,
                                         text=f'Текст {index}')
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def news_home_url():
    return reverse('news:home')


@pytest.fixture
def users_login_url():
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    return reverse('users:logout')


@pytest.fixture
def users_signup_url():
    return reverse('users:signup')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def redirect_to_news_edit(users_login_url, news_edit_url):
    return f'{users_login_url}?next={news_edit_url}'


@pytest.fixture
def redirect_to_news_delete(users_login_url, news_delete_url):
    return f'{users_login_url}?next={news_delete_url}'


@pytest.fixture
def redirect_to_news_detail(users_login_url, news_detail_url):
    return f'{users_login_url}?next={news_detail_url}'


@pytest.fixture
def redirect_to_comments(news_detail_url):
    return f'{news_detail_url}#comments'
