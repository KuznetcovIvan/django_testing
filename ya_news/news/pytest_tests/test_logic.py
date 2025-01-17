from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, id_for_args, form_data):
    """
    Тест проверяюший что анонимный пользователь
    не может создать комментарий.
    """
    url = reverse('news:detail', args=id_for_args)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(client.post(url, data=form_data), expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(reader_client, id_for_args,
                                 form_data, news, reader):
    """
    Тест проверяюший что авторизированный
    пользователь может создать комментарий.
    """
    url = reverse('news:detail', args=id_for_args)
    response = reader_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == reader


def test_user_cant_use_bad_words(reader_client, id_for_args, bad_words_data):
    """
    Тест проверяет что пользователь в коментарии
    не может использовать запрещенные слова.
    """
    assertFormError(reader_client.post(
        reverse('news:detail', args=id_for_args), data=bad_words_data),
        form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment,
                                 form_data, id_for_args):
    """
    Тест проверяющий что автор
    может изменить свой комментарий.
    """
    assertRedirects(author_client.post(
        reverse('news:edit', args=(comment.id,)), data=form_data),
        (reverse('news:detail', args=id_for_args)) + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_reader_cant_edit_comment(reader_client, comment, form_data):
    """
    Тест проверяющий что пользователь
    не может изменить чужой комментарий.
    """
    assert reader_client.post(
        reverse('news:edit', args=(comment.id,)), data=form_data
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_author_can_delete_note(author_client, comment, id_for_args):
    """
    Тест проверяющий что пользователь
    может удалить свой комментарий.
    """
    assertRedirects(author_client.post(
        reverse('news:delete', args=(comment.id,))),
        (reverse('news:detail', args=id_for_args)) + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(reader_client, comment):
    """
    Тест проверяющий что пользователь
    не может удалить чужой комментарий.
    """
    assert reader_client.post(reverse(
        'news:delete', args=(comment.id,))).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
