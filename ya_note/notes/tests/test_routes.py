from http import HTTPStatus

import notes.tests.conftest as conf


class TestRoutes(conf.TestBase):
    """
    Набор тестов для проверки доступности
    маршрутов приложения notes.
    """

    def test_pages_availability(self):
        """
        Тест проверяет доступность страниц
        различным категориям пользователей.
        """
        for url, client, expected_status in (
            (conf.ADD_URL, self.author_client, HTTPStatus.OK),
            (conf.ADD_URL, self.client, HTTPStatus.FOUND),
            (conf.DELETE_URL, self.author_client, HTTPStatus.OK),
            (conf.DELETE_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (conf.DELETE_URL, self.client, HTTPStatus.FOUND),
            (conf.DETAIL_URL, self.author_client, HTTPStatus.OK),
            (conf.DETAIL_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (conf.DETAIL_URL, self.client, HTTPStatus.FOUND),
            (conf.EDIT_URL, self.author_client, HTTPStatus.OK),
            (conf.EDIT_URL, self.not_author_client, HTTPStatus.NOT_FOUND),
            (conf.EDIT_URL, self.client, HTTPStatus.FOUND),
            (conf.HOME_URL, self.client, HTTPStatus.OK),
            (conf.LIST_URL, self.author_client, HTTPStatus.OK),
            (conf.LIST_URL, self.client, HTTPStatus.FOUND),
            (conf.LOGIN_URL, self.client, HTTPStatus.OK),
            (conf.LOGOUT_URL, self.client, HTTPStatus.OK),
            (conf.SIGNUP_URL, self.client, HTTPStatus.OK),
            (conf.SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (conf.SUCCESS_URL, self.client, HTTPStatus.FOUND),
        ):
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """
        Тест редиректа. При попытке анонимного пользователя зайти
        на страницы, предназначенные для авторизованных пользователей,
        он должен быть перенаправлен на страницу входа в учетную запись.
        """
        for url, redirect_url in (
            (conf.SUCCESS_URL, conf.REDIRECT_TO_SUCCESS),
            (conf.ADD_URL, conf.REDIRECT_TO_ADD),
            (conf.DETAIL_URL, conf.REDIRECT_TO_DETAIL),
            (conf.EDIT_URL, conf.REDIRECT_TO_EDIT),
            (conf.DELETE_URL, conf.REDIRECT_TO_DELETE),
            (conf.LIST_URL, conf.REDIRECT_TO_LIST),
        ):
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url), redirect_url)
