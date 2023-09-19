# Generated by Django 4.0.3 on 2023-09-16 05:43

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('board', '0005_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent_comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='board.comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='voter',
            field=models.ManyToManyField(related_name='voted_comment', to=settings.AUTH_USER_MODEL),
        ),
    ]
