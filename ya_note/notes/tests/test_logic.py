from http import HTTPStatus

import notes.tests.conftest as conf
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


class TestNoteCreateEditDelete(conf.TestBase):
    """
    Набор тестов для проверки логики
    создания, заметок
    """

    def create_note(self, slug):
        """
        Метод создаёт заметку от имени автора и проверяет
        соответствие атрибутов исходным данным.
        """
        notes_ids = (list(Note.objects.all().values_list('id', flat=True)))
        self.assertRedirects(self.author_client.post(
            conf.ADD_URL, data=self.form_data), conf.SUCCESS_URL)
        new_notes = Note.objects.exclude(id__in=notes_ids)
        self.assertEqual(new_notes.count(), 1)
        note = new_notes.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, slug)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """
        Тест проверяющий что анонимный пользователь
        не может создать заметку.
        """
        notes = set(Note.objects.all())
        self.client.post(conf.ADD_URL, data=self.form_data)
        self.assertEqual(set(Note.objects.all()), notes)

    def test_user_can_create_note(self):
        """
        Тест проверяющий что авторизированный пользователь
        может создать заметку.
        """
        self.create_note(self.form_data['slug'])

    def test_auto_generated_slug_if_not_provided(self):
        """
        Тест проверяет, что если в форме не указан slug, то он
        добавляется автоматически.
        """
        self.form_data.pop('slug')
        self.create_note(slugify(self.form_data['title']))

    def test_user_cant_create_note_with_non_unique_slug(self):
        """
        Тест проверяет, что пользователь не может создать заметку
        с уже использованным slug.
        """
        self.form_data['slug'] = self.note.slug
        original_notes = set(Note.objects.all())
        self.assertFormError(
            self.author_client.post(conf.ADD_URL, data=self.form_data),
            form='form',
            field='slug',
            errors=self.note.slug + WARNING)
        self.assertEqual(set(Note.objects.all()), original_notes)

    def test_author_can_edit_note(self):
        """
        Тест проверяющий что автор
        может редактировать свою заметку.
        """
        self.assertRedirects(self.author_client.post(
            conf.EDIT_URL, data=self.form_data), conf.SUCCESS_URL)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_edit_note(self):
        """
        Тест проверяющий что пользователь
        не может редактировать чужую заметку.
        """
        self.assertEqual(self.not_author_client.post(
            conf.EDIT_URL, data=self.form_data).status_code,
            HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_note(self):
        """
        Тест проверяющий
        что автор может удалить свою заметку.
        """
        original_count = Note.objects.count()
        self.assertRedirects(self.author_client.delete(
            conf.DELETE_URL), conf.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), original_count - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cant_delete_note_of_another_user(self):
        """
        Тест проверяющий что пользователь
        не может удалить чужую заметку.
        """
        original_count = Note.objects.count()
        self.assertEqual(self.not_author_client.delete(
            conf.DELETE_URL).status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), original_count)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
