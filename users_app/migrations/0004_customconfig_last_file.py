# Generated by Django 4.0.5 on 2022-12-29 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users_app", "0003_alter_customconfig_default_storage_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customconfig",
            name="last_file",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
