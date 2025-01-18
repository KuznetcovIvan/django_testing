from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

NEWS_HOME_URL = pytest.lazy_fixture('news_home_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
USERS_LOGIN_URL = pytest.lazy_fixture('users_login_url')
USERS_LOGOUT_URL = pytest.lazy_fixture('users_logout_url')
USERS_SIGNUP_URL = pytest.lazy_fixture('users_signup_url')
NEWS_EDIT_URL = pytest.lazy_fixture('news_edit_url')
NEWS_DELETE_URL = pytest.lazy_fixture('news_delete_url')
REDIRECT_TO_NEWS_EDIT = pytest.lazy_fixture('redirect_to_news_edit')
REDIRECT_TO_NEWS_DELETE = pytest.lazy_fixture('redirect_to_news_delete')

CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')


@pytest.mark.parametrize('url, parametrized_client, expected_status', (
    (NEWS_HOME_URL, CLIENT, HTTPStatus.OK),
    (NEWS_DETAIL_URL, CLIENT, HTTPStatus.OK),
    (USERS_LOGIN_URL, CLIENT, HTTPStatus.OK),
    (USERS_LOGOUT_URL, CLIENT, HTTPStatus.OK),
    (USERS_SIGNUP_URL, CLIENT, HTTPStatus.OK),
    (NEWS_EDIT_URL, CLIENT, HTTPStatus.FOUND),
    (NEWS_DELETE_URL, CLIENT, HTTPStatus.FOUND),
    (NEWS_EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    (NEWS_DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    (NEWS_EDIT_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
    (NEWS_DELETE_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
))
def test_pages_availability(url, parametrized_client, expected_status):
    """
    Тест проверяет доступность страниц
    различным категориям пользователей.
    """
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize('url, redirect_url', (
    (NEWS_EDIT_URL, REDIRECT_TO_NEWS_EDIT,),
    (NEWS_DELETE_URL, REDIRECT_TO_NEWS_DELETE)
))
def test_redirects(client, url, redirect_url):
    """
    Тест редиректа. При попытке анонимного пользователя зайти
    на страницы, предназначенные для авторизованных пользователей,
    он должен быть перенаправлен на страницу входа в учетную запись.
    """
    assertRedirects(client.get(url), redirect_url)
