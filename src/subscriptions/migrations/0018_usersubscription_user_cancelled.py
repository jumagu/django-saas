# Generated by Django 5.0.8 on 2024-12-15 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0017_usersubscription_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='user_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
