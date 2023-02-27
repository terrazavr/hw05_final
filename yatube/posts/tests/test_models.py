from django.test import TestCase
from django.conf import settings

from posts.models import Group, Post, User
from posts.tests.constants import (
    GROUP_DESCRIPTION,
    GROUP_SLUG,
    GROUP_TITLE,
    POST_TEXT,
)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=GROUP_DESCRIPTION,
            slug=GROUP_SLUG,
            description=GROUP_TITLE,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        data = {
            'post': (
                str(self.post),
                self.post.text[:settings.LEN_TEXT]
            ),
            'group': (
                str(self.group),
                self.group.title
            ),
        }

        for key, value in data.items():
            actual_value, expected = value
            with self.subTest(
                model=key, expected=expected, actual_value=actual_value
            ):
                self.assertEqual(expected, actual_value,
                                 'строковое отображение не работает')

    def test_verbose_name(self):
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
