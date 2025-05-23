# Generated by Django 4.2.20 on 2025-04-28 21:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kwai', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kwai',
            name='user_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kwai_entries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='kwai',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
