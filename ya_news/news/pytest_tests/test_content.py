from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm


@pytest.mark.usefixtures('news_collection')
@pytest.mark.django_db()
def test_news_count(client):
    """
    Тест для проверки количества объектов (новостей)
    выводимых на главную страницу (не более 10).
    """
    assert client.get(reverse('news:home')).context['object_list'].count() == \
        settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db()
def test_news_order(client):
    """
    Тест для проверки сортировки отображаемых
    новостей (от самой свежей к самой старой).
    """
    all_dates = [news.date for news in
                 client.get(reverse('news:home')).context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db()
def test_comments_order(client, id_for_args):
    """
    Тест для проверки сортировки отображаемых
    коментариев (от старых к новым).
    """
    response = client.get(reverse('news:detail', args=id_for_args))
    assert 'news' in response.context
    all_timestamps = [comment.created for comment in
                      response.context['news'].comment_set.all()]
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
