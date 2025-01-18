import notes.tests.conftest as conf
from notes.forms import NoteForm


class TestNotesList(conf.TestBase):
    """
    Набор тестов для проверки
    содержимого страниц.
    """

    def test_author_can_see_own_notes(self):
        """
        Тест проверяет, что на странице отображаются заметки
        текущего авторизированного пользователя.
        """
        notes = self.author_client.get(
            conf.LIST_URL).context['object_list']
        self.assertTrue(notes.filter(id=self.note.id).exists())
        note = notes.get(id=self.note.id)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)

    def test_other_users_cannot_see_notes(self):
        """
        Тест проверяет, что на странице не отображаются заметки
        других пользователей.
        """
        self.assertNotIn(
            self.note,
            self.not_author_client.get(conf.LIST_URL).context['object_list']
        )

    def test_authorized_client_has_valid_form(self):
        """
        Тест для проверки что авторизированному пользователю
        на странице создания и редактирования заметки видна нужная форма.
        """
        for url in (conf.ADD_URL, conf.EDIT_URL):
            with self.subTest(url=url):
                self.assertIsInstance(self.author_client.get(
                    url).context.get('form'), NoteForm)
