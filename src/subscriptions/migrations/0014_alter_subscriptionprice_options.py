# Generated by Django 5.0.8 on 2024-12-13 04:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0013_alter_subscription_options_subscription_featured_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptionprice',
            options={'ordering': ['subscription__order', 'order', 'featured', '-updated']},
        ),
    ]