# Generated by Django 4.2.2 on 2023-06-11 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("brainservice", "0002_channel_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="email",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
