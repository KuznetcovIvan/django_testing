from django.urls import reverse
from django.conf import settings

import pytest

from news.forms import CommentForm


@pytest.mark.usefixtures('news_collection')
@pytest.mark.django_db()
def test_news_count(client):
    """
    Тест для проверки количества объектов (новостей)
    выводимых на главную страницу
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db()
def test_news_order(client):
    """
    Тест для проверки сортировки отображаемых
    новостей (от самой свежей к самой старой).
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db()
def test_comments_order(client, id_for_args):
    """
    Тест для проверки сортировки отображаемых
    коментариев (от старых к новым).
    """
    url = reverse('news:detail', args=id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.django_db()
@pytest.mark.parametrize('parametrize_client, is_form_visible', (
                         (pytest.lazy_fixture('client'), False),
                         (pytest.lazy_fixture('reader_client'), True)))
def test_authorized_client_has_form(id_for_args,
                                    parametrize_client,
                                    is_form_visible):
    """
    Тест для проверки что только авторизованному пользователю на
    странице новости видна форма для создания комментариев.
    """
    response = parametrize_client.get(reverse('news:detail', args=id_for_args))
    assert ('form' in response.context) == is_form_visible
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
