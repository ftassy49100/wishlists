# Generated by Django 4.0.1 on 2022-03-08 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0004_idea_booked_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]