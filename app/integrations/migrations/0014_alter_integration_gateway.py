# Generated by Django 4.2.20 on 2025-03-20 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0013_integrationsample'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integration',
            name='gateway',
            field=models.CharField(choices=[('zeroone', 'ZeroOne'), ('ghostspay', 'GhostsPay'), ('paradisepag', 'ParadisePag'), ('disrupty', 'Disrupty'), ('wolfpay', 'WolfPay'), ('vegacheckout', 'VegaCheckout'), ('cloudfy', 'CloudFy'), ('tribopay', 'TriboPay'), ('westpay', 'WestPay')], max_length=255),
        ),
    ]
