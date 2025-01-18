from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note, User

NOTE_SLUG = 'note_slug'


class TestBase(TestCase):
    """
    Базовый класс тестов,
    содержащий общий набор фикстур.
    """
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст заметки',
                                       slug=NOTE_SLUG,
                                       author=cls.author)

        cls.form_data = {'title': 'Новый заголовок',
                         'text': 'Новый текст заметки',
                         'slug': 'new_slug'}


ADD_URL = reverse('notes:add')
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')

REDIRECT_TO_SUCCESS = f'{LOGIN_URL}?next={SUCCESS_URL}'
REDIRECT_TO_ADD = f'{LOGIN_URL}?next={ADD_URL}'
REDIRECT_TO_DETAIL = f'{LOGIN_URL}?next={DETAIL_URL}'
REDIRECT_TO_EDIT = f'{LOGIN_URL}?next={EDIT_URL}'
REDIRECT_TO_DELETE = f'{LOGIN_URL}?next={DELETE_URL}'
REDIRECT_TO_LIST = f'{LOGIN_URL}?next={LIST_URL}'
