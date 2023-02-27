import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


from posts.models import Post, Group, User, Follow

from posts.tests.constants import (
    POST_IN_PAGE,
    POST_IN_2PAGE,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
    POST_TEXT,
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            image=cls.uploaded
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.client.get(reverse(INDEX_URL_NAME))
        expected = Post.objects.all()[0]
        self.assertEqual(response.context['page_obj'][0], expected)
        self.assertContains(response, '<img')

    def test_group_post_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.client.get(reverse(GROUP_LIST_URL_NAME,
                                           kwargs={'slug': self.group.slug}))
        expected = list(Post.objects.filter(group_id=self.group.id))
        self.assertEqual(list(response.context['page_obj']), expected)
        self.assertContains(response, '<img')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.client.get(
            reverse(PROFILE_URL_NAME, kwargs={'username': self.user.username}))
        expected = list(Post.objects.filter(author_id=self.user.id))
        self.assertEqual(list(response.context['page_obj']), expected)
        self.assertContains(response, '<img')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.client.get(
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'], self.post)
        self.assertContains(response, '<img')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL_NAME))

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id}))

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='usertest')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )
        Post.objects.bulk_create(
            Post(
                text=cls.post.text,
                group=cls.group,
                author=cls.user
            ) for _ in range(POST_IN_PAGE + 2)
        )

        cls.urls_list = {
            INDEX_URL_NAME: reverse(INDEX_URL_NAME),

            GROUP_LIST_URL_NAME:
                reverse(GROUP_LIST_URL_NAME,
                        kwargs={'slug': cls.group.slug}),

            PROFILE_URL_NAME:
                reverse(PROFILE_URL_NAME,
                        kwargs={'username': cls.user.username}),
        }
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Тестируем пагинатор на 1й стр."""
        for template, reverse_name in self.urls_list.items():
            response = self.client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), POST_IN_PAGE)

    def test_2nd_page_contains_three_records(self):
        """Тестируем пагинатор на 2й стр."""
        for template, reverse_name in self.urls_list.items():
            response = self.client.get(reverse_name + '?page=2')
            self.assertEqual(len(response.context['page_obj']), POST_IN_2PAGE)


class PostGroupInTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='usertest')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст2',
            group=cls.group_2,
        )
        cache.clear()

    def test_post_in_page(self):
        urls_list = {
            INDEX_URL_NAME: reverse(INDEX_URL_NAME),

            GROUP_LIST_URL_NAME:
                reverse(GROUP_LIST_URL_NAME,
                        kwargs={'slug': self.group_2.slug}),

            PROFILE_URL_NAME:
                reverse(PROFILE_URL_NAME,
                        kwargs={'username': self.user.username}),
        }

        for value in urls_list.values():
            response = self.client.get(value)
            object_list = response.context.get('page_obj').object_list
            post = Post.objects.first()
            self.assertIn(post, object_list)

    def test_post_not_in_page_group(self):
        response = self.client.get(
            reverse(GROUP_LIST_URL_NAME, kwargs={'slug': self.group.slug}))
        object_list = response.context.get('page_obj').object_list
        post = Post.objects.first()
        self.assertNotIn(post, object_list)

    def cache_test(self):
        response = self.client.get(reverse('posts:index'))
        content = response.content

        Post.objects.all().delete()

        response1 = self.client.get(reverse('posts:index'))
        content1 = response1.content

        self.assertEqual(content, content1)

        cache.clear()

        response2 = self.client.get(reverse('posts:index'))
        content2 = response2.content

        self.assertNotEqual(content, content2)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='usertest')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.create_user(username='usi')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user)

    def test_following_for_auth_client(self):
        """Авторизованный пользователь может подписаться на автора"""
        follows_count = Follow.objects.count()
        self.authorized_client2.get(reverse('posts:profile_follow',
                                            kwargs={'username': 'usi'}))
        self.assertEqual(Follow.objects.count(), follows_count + 1)

    def test_post_in_follower_wall_and_not_in_not_follower_wall(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан."""
        new_post_follower = Post.objects.create(
            author=self.user,
            text='Текстовый текст')
        Follow.objects.create(user=self.user,
                              author=self.user)
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        new_posts = response_follower.context['page_obj']
        self.assertIn(new_post_follower, new_posts)

    def test_follower_see_new_post(self):
        """Новый пост не появляется в ленте у того,
        кто не подписан.
        """
        new_post_follower = Post.objects.create(
            author=self.user,
            text='Текстовый текст')
        Follow.objects.create(user=self.user2,
                              author=self.user)
        response_unfollower = self.authorized_client2.get(
            reverse('posts:follow_index'))
        new_post_unfollower = response_unfollower.context['page_obj']
        self.assertNotIn(new_post_follower, new_post_unfollower)
