from http import HTTPStatus

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}
BAD_WORDS_DATA = [{'text': word} for word in BAD_WORDS]


def test_anonymous_user_cant_create_comment(
    client,
    news_detail_url,
    redirect_to_news_detail
):
    """
    Тест проверяюший что анонимный пользователь
    не может создать комментарий.
    """
    assertRedirects(client.post(news_detail_url, data=FORM_DATA),
                    redirect_to_news_detail)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(reader_client, news_detail_url,
                                 redirect_to_comments,
                                 news, reader):
    """
    Тест проверяюший что авторизированный
    пользователь может создать комментарий.
    """
    assertRedirects(reader_client.post(news_detail_url, data=FORM_DATA),
                    redirect_to_comments)
    assert Comment.objects.count() == 1

    comment_from_db = Comment.objects.get()
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.news == news
    assert comment_from_db.author == reader


@pytest.mark.parametrize('bad_words_data', BAD_WORDS_DATA)
def test_user_cant_use_bad_words(reader_client, news_detail_url,
                                 bad_words_data):
    """
    Тест проверяет что пользователь в коментарии
    не может использовать запрещенные слова.
    """
    assertFormError(reader_client.post(news_detail_url,
                                       data=bad_words_data),
                    form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment,
                                 news_edit_url, redirect_to_comments):
    """
    Тест проверяющий что автор
    может изменить свой комментарий.
    """
    assertRedirects(author_client.post(news_edit_url, data=FORM_DATA),
                    redirect_to_comments)
    comment_from_db = Comment.objects.get()
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author


def test_reader_cant_edit_comment(reader_client, comment, news_edit_url):
    """
    Тест проверяющий что пользователь
    не может изменить чужой комментарий.
    """
    assert (reader_client.post(news_edit_url, data=FORM_DATA).status_code
            == HTTPStatus.NOT_FOUND)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_author_can_delete_note(author_client, redirect_to_comments,
                                news_delete_url):
    """
    Тест проверяющий что пользователь
    может удалить свой комментарий.
    """
    assertRedirects(author_client.post(news_delete_url),
                    redirect_to_comments)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(reader_client, news_delete_url, comment):
    """
    Тест проверяющий что пользователь
    не может удалить чужой комментарий.
    """
    assert (reader_client.post(news_delete_url).status_code
            == HTTPStatus.NOT_FOUND)
    assert Comment.objects.filter(id=comment.id).exists()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
