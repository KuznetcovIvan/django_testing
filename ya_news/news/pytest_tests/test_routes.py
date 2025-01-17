from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize('name, args',
                         (('news:home', None),
                          ('news:detail', pytest.lazy_fixture('id_for_args')),
                          ('users:login', None),
                          ('users:logout', None),
                          ('users:signup', None)),)
def test_pages_availability(client, name, args):
    """
    Тест проверяет доступность страниц
    анонимному пользователю.
    """
    assert client.get(reverse(name, args=args)).status_code == HTTPStatus.OK


@pytest.mark.parametrize('parametrized_client, expected_status', (
    (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)))
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_availability_for_comment_edit_and_delete(parametrized_client,
                                                  expected_status,
                                                  comment, name):
    """
    Тест проверяет, что:
    Автор может зайти на страницу редактирования своего комментария.
    Автор может зайти на страницу удаления своего комментария.
    Читатель этого сделать не может.
    """
    assert parametrized_client.get(
        reverse(name, args=(comment.id,))).status_code == expected_status


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirects(client, name, comment):
    """
    Тест редиректа. При попытке анонимного пользователя зайти
    на страницы, предназначенные для авторизованных пользователей,
    он должен быть перенаправлен на страницу входа в учетную запись.
    """
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{reverse("users:login")}?next={url}'
    assertRedirects(client.get(url), redirect_url)
