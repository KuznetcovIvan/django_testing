from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note, User


class TestNoteCreateEditDelete(TestCase):
    """
    Набор тестов для проверки логики
    создания, заметок
    """
    NOTE_SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя
        cls.user = User.objects.create(username='Пользователь')
        # Создаём клиент для пользователя:
        cls.user_client = Client()
        # Авторизируем пользователя:
        cls.user_client.force_login(cls.user)

        # Набор данных для формы создания заметки:
        cls.form_data_without_slug = {'title': 'Заметка',
                                      'text': 'Текст заметки'}
        cls.form_data = cls.form_data_without_slug | {'slug': cls.NOTE_SLUG}

        # Страница создания заметки.
        cls.add_url = reverse('notes:add')
        # Страница успешного выполнения.
        cls.success_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        """
        Тест проверяющий что анонимный пользователь
        не может создать заметку.
        """
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """
        Тест проверяющий что авторизированный пользователь
        может создать заметку.
        """
        response = self.user_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_user_cant_create_note_with_non_unique_slug(self):
        """
        Тест проверяет, что пользователь не может создать заметку
        с уже использованным slug.
        """
        Note.objects.create(title='Заметка',
                            text='Текст заметки',
                            slug=self.NOTE_SLUG,
                            author=self.user)

        response = self.user_client.post(self.add_url, data=self.form_data)
        self.assertFormError(response,
                             form='form',
                             field='slug',
                             errors=self.NOTE_SLUG + WARNING)

    def test_auto_generated_slug_if_not_provided(self):
        """
        Тест проверяет, что если в форме не указан slug, то он
        добавляется автоматически.
        """
        self.user_client.post(self.add_url, data=self.form_data_without_slug)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        notes_slug = Note.objects.get().slug
        self.assertEqual(notes_slug,
                         slugify(self.form_data_without_slug['title']))


class TestNoteEditDelete(TestCase):
    """
    Набор тестов проверяющих
    редактирование и удаление заметок.
    """
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей:
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        # Создаём клиенты для пользователей:
        cls.author_client = Client()
        cls.not_author_client = Client()
        # Авторизируем клиенты:
        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)

        # От лица автора создаём заметку:
        cls.note = Note.objects.create(author=cls.author,
                                       title='Заголовок',
                                       text=cls.NOTE_TEXT,
                                       slug='note_1')
        # Страница создания заметки.
        cls.add_url = reverse('notes:add')
        # Страница редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # Страница удаления заметки.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Страница успешного выполнения.
        cls.success_url = reverse('notes:success')

        # Готовим данные для отправки post запроса на изменение заметки:
        cls.form_data = {'title': 'Заголовок',
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': 'note_1'}

    def test_author_can_delete_note(self):
        """
        Тест проверяющий
        что автор может удалить свою заметку.
        """
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """
        Тест проверяющий что пользователь
        не может удалить чужую заметку.
        """
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """
        Тест проверяющий что автор
        может изменить свою заметку.
        """
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note(self):
        """
        Тест проверяющий что пользователь не может редактировать
        чужую заметку.
        """
        response = self.not_author_client.post(self.edit_url,
                                               data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
