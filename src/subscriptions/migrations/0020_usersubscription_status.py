# Generated by Django 5.0.8 on 2024-12-15 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0019_usersubscription_current_period_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'Active'), ('trialing', 'Trialing'), ('incomplete', 'Incomplete'), ('incomplete_expired', 'Incomplete Expired'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('unpaid', 'Unpaid'), ('paused', 'Paused')], max_length=20, null=True),
        ),
    ]
