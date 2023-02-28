from django.forms import ModelForm, Textarea

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')

        labels = {
            'text': 'Tекст поста',
            'group': 'Группа',
            'image': 'Картинка'}

        help_texts = {
            'text': 'Текст нового поста, не оставляй его пустым',
            'group': 'Выбери группу или оставьте поле пустым'}

        widgets = {
            'text': Textarea(attrs={'class': 'form-control',
                                    'placeholder': 'Текст тут'}),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'text': Textarea(attrs={'class': 'form-control',
                                    'placeholder': 'Комментарий тут'})
        }
