from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note, User


class TestRoutes(TestCase):
    """
    Набор тестов для проверки доступности
    маршрутов приложения notes.
    """
    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей:
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Читатель')
        # Создаём клиенты для пользователей:
        cls.author_client = Client()
        cls.not_author_client = Client()
        # Авторизируем клиенты:
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)
        # От лица автора создаём заметку:
        cls.note = Note.objects.create(author=cls.author,
                                       title='Заголовок',
                                       text='Текст',
                                       slug='note_1')

        # Страница создания заметки.
        cls.add_url = reverse('notes:add')
        # Страница удаления заметки.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Страница заметки подробно.
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        # Страница редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # Домашняя страница.
        cls.home_url = reverse('notes:home')
        # Страница всех заметок.
        cls.list_url = reverse('notes:list')
        # Страница успешного выполнения.
        cls.success_url = reverse('notes:success')
        # Страница входа под учётной записью.
        cls.login_url = reverse('users:login')
        # Страница выхода из учётной записи.
        cls.logout_url = reverse('users:logout')
        # Страница регистрации.
        cls.signup_url = reverse('users:signup')

    def test_pages_availability(self):
        """
        Тест проверяет доступность страниц
        анонимному пользователю.
        """
        for url in (self.home_url,
                    self.login_url,
                    self.logout_url,
                    self.signup_url,):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """
        Тест проверяет доступность страниц просмотра, редактирования
        и удаления заметки автору (и недоступность не автору).
        """
        client_statuses = ((self.author_client, HTTPStatus.OK),
                           (self.not_author_client, HTTPStatus.NOT_FOUND))

        for client, status in client_statuses:
            for url in (self.detail_url,
                        self.edit_url,
                        self.delete_url):
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_add_list_and_success(self):
        """
        Тест проверяет доступность страниц
        добавления заметки, списка заметок, успешного выполнения
        для авторизированного пользователя (и недоступность анонимному
        пользователю).
        """
        client_status = ((self.client, HTTPStatus.FOUND),
                         (self.author_client, HTTPStatus.OK))

        for client, status in client_status:
            for url in (self.add_url,
                        self.list_url,
                        self.success_url):
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Тест редиректа. При попытке анонимного пользователя зайти
        на страницы, предназначенные для авторизованных пользователей,
        он должен быть перенаправлен на страницу входа в учетную запись.
        """
        for url in (self.success_url,
                    self.add_url,
                    self.detail_url,
                    self.edit_url,
                    self.delete_url,
                    self.list_url):
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
