# Generated by Django 5.1.5 on 2025-01-22 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_rename_user_liked_image_users_like_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='url',
            field=models.URLField(blank=True, max_length=2000),
        ),
    ]
