from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0017_alter_campaign_roi_alter_campaign_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='total_refunded',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='amount_refunded',
            field=models.DecimalField(decimal_places=2, max_digits=20, default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='total_rejected',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='amount_rejected',
            field=models.DecimalField(decimal_places=2, max_digits=20, default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='total_chargeback',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='amount_chargeback',
            field=models.DecimalField(decimal_places=2, max_digits=20, default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='total_abandoned',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='campaign',
            name='amount_abandoned',
            field=models.DecimalField(decimal_places=2, max_digits=20, default=0),
        ),
    ]