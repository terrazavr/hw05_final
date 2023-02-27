import shutil
import tempfile

from http import HTTPStatus

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User, Comment
from posts.tests.constants import (
    POST_CREATE_URL_NAME,
    PROFILE_URL_NAME,
    POST_EDIT_URL_NAME,
    GROUP_DESCRIPTION,
    GROUP_SLUG,
    GROUP_TITLE,
    POST_TEXT,
    COMMENTS_URL,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Me')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group
        )


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='You')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """При отправке валидной формы создается запись в БД."""
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertRedirects(response, reverse(
            PROFILE_URL_NAME, kwargs={'username': self.user.username}))

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(Post.objects.filter(
            text=self.post.text,
            group=self.group.id,
            image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """После редактирования сохраняется новый пост."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'New text of post',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse(POST_EDIT_URL_NAME, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(Post.objects.count(), posts_count)

        self.assertTrue(Post.objects.filter(
            text=self.post.text,
            group=self.group.id,
            pub_date=self.post.pub_date).exists()
        )

    def test_guest_cant_create_post(self):
        """Неавторизованный юзер не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.client.post(
            reverse(POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

        self.assertEqual(Post.objects.count(), posts_count)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Me')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            text='Comment text',
            author=cls.user,
            post_id=cls.post.id,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='You')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        comments_count = Comment.objects.count()
        form_datas = {
            'post_id': self.post.id,
            'text': 'Второй комментарий'
        }
        response = self.authorized_client.post(
            reverse(COMMENTS_URL, kwargs={'post_id': self.post.id}),
            data=form_datas,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(Comment.objects.count(), comments_count + 1)

        self.assertTrue(Comment.objects.filter(
            text='Второй комментарий',
            post=self.post.id,
            author=self.user).exists()
        )

    def test_guest_cant_comment_post(self):
        """Неавторизованный юзер не может создать комментарий."""
        comments_count = Comment.objects.count()
        form_datas = {
            'post_id': self.post.id,
            'text': '3 комментарий'
        }
        response = self.client.post(
            reverse(COMMENTS_URL, kwargs={'post_id': self.post.id}),
            data=form_datas,
            follow=True,
        )
        redirect_url = f'/auth/login/?next=/posts/{self.post.id}/comment/'

        self.assertRedirects(response, redirect_url)

        self.assertEqual(Comment.objects.count(), comments_count)
