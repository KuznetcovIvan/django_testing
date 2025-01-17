from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note, User


class TestNotesList(TestCase):
    """
    Набор тестов для проверки содержимого
    страницы, содержащей все заметки пользователя.
    """
    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')

        cls.author_client = Client()
        cls.not_author_client = Client()

        cls.author_client.force_login(cls.author)
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(title='Зметка',
                                       text='Текст',
                                       slug='note_slug',
                                       author=cls.author)

        cls.list_url = reverse('notes:list')

    def test_only_authenticated_user_notes_displayed(self):
        """
        Тест проверяет, что на странице отображаются заметки
        только текущего авторизированного пользователя
        (чужие заметки не отображаются).
        """
        client_note_in_list = ((self.author_client, True),
                               (self.not_author_client, False))

        for client, note_in_list in client_note_in_list:
            with self.subTest(client=client):
                self.assertEqual(self.note in client.get(
                    self.list_url).context['object_list'], note_in_list)


class TestNoteCreate(TestCase):
    """
    Набор тестов для проверки содержимого
    страниц создания и редактирования заметки.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.note = Note.objects.create(title='Заметка',
                                       text='Текст',
                                       slug='note_slug',
                                       author=cls.user)

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_valid_form(self):
        """
        Тест для проверки что авторизированному пользователю
        на странице создания и редактирования заметки видна нужная форма.
        """
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
