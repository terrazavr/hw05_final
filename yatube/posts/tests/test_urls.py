from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group, User
from posts.tests.constants import (
    GROUP_DESCRIPTION,
    GROUP_SLUG,
    GROUP_TITLE,
    POST_TEXT,
    INDEX_URL_NAME,
    GROUP_LIST_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_EDIT_URL_NAME,
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_EDIT_TEMPLATE,
    COMMENTS_URL,
)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_home_url_exists_at_desire_location(self):
        """ Страница доступна любому пользователю."""
        response = self.client.get(reverse(INDEX_URL_NAME))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_exists_at_desire_location(self):
        """ Страница груп лист доступна любому пользователю."""
        response = self.client.get(
            reverse(GROUP_LIST_URL_NAME, kwargs={'slug': self.group.slug}))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_exists_at_desire_location(self):
        """ Страница профиля доступна любому пользователю."""
        response = self.client.get(
            reverse(PROFILE_URL_NAME, kwargs={'username': self.user.username}))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_exists_at_desire_location(self):
        """ Страница отдельного поста доступна любому пользователю."""
        response = self.client.get(
            reverse(POST_DETAIL_URL_NAME, kwargs={'post_id': self.post.id}))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Тесты для авторизованных пользователей
    def test_create_page(self):
        """ Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_page(self):
        """ Страница редактирования поста доступна только автору."""
        response = self.authorized_client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id}))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Тест страницы 404
    def test_unexisting_page_404(self):
        """ Страница 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_comments(self):
        """Комментарии недоступны гостю."""
        response = self.client.get(COMMENTS_URL,
                                   kwargs={'post_id': self.post.id})
        self.assertEqual(response.status_code, 404)

    # Тесты с редиректами пользователей без определенных прав
    def test_create_url_redirect_anon_on_login(self):
        """ Страница создания поста перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_non_athor_on_post_detail(self):
        """ Страница редактирования поста перенаправит не
        автора поста страницу самого поста.
        """
        response = self.client.get(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': 1}),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        redirect_url = (
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(response, redirect_url)

    # Тесты шаблонов
    def test_urls_uses_rigth_template(self):
        """URL - адреса используют верный шаблон."""
        urls_templates = {
            '/': INDEX_TEMPLATE,
            f'/group/{self.group.slug}/': GROUP_LIST_TEMPLATE,
            f'/profile/{self.user.username}/': PROFILE_TEMPLATE,
            f'/posts/{self.post.id}/': POST_DETAIL_TEMPLATE,
            '/create/': POST_CREATE_EDIT_TEMPLATE,
            f'/posts/{self.post.id}/edit/': POST_CREATE_EDIT_TEMPLATE,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
