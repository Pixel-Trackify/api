# Generated by Django 4.2.20 on 2025-03-28 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0021_alter_campaign_amount_approved_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='amount_abandoned',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='amount_approved',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='amount_canceled',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='amount_chargeback',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='amount_pending',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='amount_refunded',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='amount_rejected',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]
