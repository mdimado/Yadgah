# Generated by Django 4.2.18 on 2025-01-24 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0021_question_view_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="score",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
