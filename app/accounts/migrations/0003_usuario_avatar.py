# Generated by Django 4.2.20 on 2025-03-25 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='avatar',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
