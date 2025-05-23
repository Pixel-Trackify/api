# Generated by Django 4.2.20 on 2025-03-21 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0015_alter_integration_gateway'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integration',
            name='gateway',
            field=models.CharField(choices=[('zeroone', 'ZeroOne'), ('ghostspay', 'GhostsPay'), ('paradisepag', 'ParadisePag'), ('disrupty', 'Disrupty'), ('wolfpay', 'WolfPay'), ('vegacheckout', 'VegaCheckout'), ('cloudfy', 'CloudFy'), ('tribopay', 'TriboPay'), ('westpay', 'WestPay'), ('sunize', 'Sunize'), ('grapefy', 'Grapefy')], max_length=255),
        ),
    ]
