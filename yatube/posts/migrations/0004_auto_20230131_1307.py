# Generated by Django 2.2.9 on 2023-01-31 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20230123_0501'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
    ]
