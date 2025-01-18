import pytest
from django.conf import settings
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_home_url, news_collection):
    """
    Тест для проверки количества объектов (новостей)
    выводимых на главную страницу (не более 10).
    """
    assert (client.get(news_home_url).context['object_list'].count()
            == settings.NEWS_COUNT_ON_HOME_PAGE)


def test_news_order(client, news_home_url):
    """
    Тест для проверки сортировки отображаемых
    новостей (от самой свежей к самой старой).
    """
    all_dates = [news.date for news in
                 client.get(news_home_url).context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, news_detail_url):
    """
    Тест для проверки сортировки отображаемых
    коментариев (от старых к новым).
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_timestamps = [comment.created for comment in
                      response.context['news'].comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


def test_authorized_user_has_form(news_detail_url, reader_client):
    """
    Тест для проверки, что только авторизованному пользователю на
    странице новости видна форма для создания комментариев.
    """
    assert isinstance(reader_client.get(
        news_detail_url).context.get('form'), CommentForm)


def test_anonymous_user_does_not_have_form(news_detail_url, client):
    """
    Тест для проверки, что неавторизованный пользователь на
    странице новости не видит форму для создания комментариев.
    """
    assert 'form' not in client.get(news_detail_url).context
