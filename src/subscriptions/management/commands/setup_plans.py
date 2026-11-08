from decimal import Decimal

import stripe
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand, CommandError
from django.db import transaction

import helpers.billing  # noqa: F401 (sets stripe.api_key)
from subscriptions import utils as subs_utils
from subscriptions.models import Subscription, SubscriptionPrice

# Products and prices that already exist in the Stripe test account
PLANS = [
    {
        'name': 'Starter',
        'stripe_id': 'prod_RODKChCpcGMmBu',
        'subtitle': 'Everything you need to get started on your own.',
        'features': ['1 user', '3 projects', 'Basic analytics', 'Email support'],
        'permissions': ['basic'],
        'prices': [
            {'interval': 'month', 'price': '49.99', 'stripe_id': 'price_1QVc0vKBY9GuWSwBbSaSh3KR'},
            {'interval': 'year', 'price': '499.99', 'stripe_id': 'price_1QVbyrKBY9GuWSwBQP8lsSnZ'},
        ],
    },
    {
        'name': 'Pro',
        'stripe_id': 'prod_RODLYR9wRATZDH',
        'subtitle': 'For small teams that need more power.',
        'features': ['Up to 5 users', 'Unlimited projects', 'Advanced analytics', 'Priority email support'],
        'permissions': ['basic', 'pro'],
        'prices': [
            {'interval': 'month', 'price': '79.99', 'stripe_id': 'price_1QVc0iKBY9GuWSwBz6tJxDgT'},
            {'interval': 'year', 'price': '799.99', 'stripe_id': 'price_1QVbzFKBY9GuWSwBpe7JuOHi'},
        ],
    },
    {
        'name': 'Enterprise',
        'stripe_id': 'prod_RJZBeDL89A0X9V',
        'subtitle': 'For organizations that need AI and dedicated support.',
        'features': [
            'Unlimited users',
            'Everything in Pro',
            'AI-powered insights',
            'Dedicated account manager',
            '24/7 phone support',
        ],
        'permissions': ['basic', 'pro', 'advanced', 'basic_ai'],
        'prices': [
            {'interval': 'month', 'price': '99.99', 'stripe_id': 'price_1QQzQuKBY9GuWSwBv1uGeSkO'},
            {'interval': 'year', 'price': '1099.99', 'stripe_id': 'price_1QQzQvKBY9GuWSwB7TFUdppt'},
        ],
    },
]


class Command(BaseCommand):
    help = (
        'Create the subscription plans, their prices and groups, reusing the products and '
        'prices that already exist in Stripe. Plans and prices that already exist are left as they are.'
    )

    def handle(self, *args, **options):
        self.check_stripe()
        with transaction.atomic():
            for order, plan_data in enumerate(PLANS, start=1):
                self.setup_plan(plan_data, order)
        subs_utils.sync_subs_group_permissions()
        self.stdout.write(self.style.SUCCESS('Plans are ready. Group permissions synced.'))

    def check_stripe(self):
        """Make sure every price exists in the configured Stripe account and matches its plan."""
        for plan_data in PLANS:
            for price_data in plan_data['prices']:
                try:
                    price = stripe.Price.retrieve(price_data['stripe_id'])
                except stripe.StripeError as e:
                    raise CommandError(f"{plan_data['name']}: could not get price {price_data['stripe_id']} from Stripe: {e}")
                expected = (plan_data['stripe_id'], int(Decimal(price_data['price']) * 100), price_data['interval'])
                actual = (price.product, price.unit_amount, price.recurring.interval if price.recurring else None)
                if actual != expected:
                    raise CommandError(f"{plan_data['name']}: price {price_data['stripe_id']} is {actual} in Stripe, expected {expected}")

    def setup_plan(self, plan_data, order):
        permissions = Permission.objects.filter(
            content_type__app_label='subscriptions',
            codename__in=plan_data['permissions'],
        )
        if permissions.count() != len(plan_data['permissions']):
            raise CommandError('Subscription permissions are missing. Run `python manage.py migrate` first.')

        group, _ = Group.objects.get_or_create(name=plan_data['name'])
        # stripe_id is set, so saving does not create a new product in Stripe
        plan, created = Subscription.objects.get_or_create(
            stripe_id=plan_data['stripe_id'],
            defaults={
                'name': plan_data['name'],
                'subtitle': plan_data['subtitle'],
                'features': '\n'.join(plan_data['features']),
                'order': order,
            },
        )
        if created:
            plan.groups.set([group])
            plan.permissions.set(permissions)
        self.stdout.write(f"{plan.name}: {'created' if created else 'already exists'}")

        for price_data in plan_data['prices']:
            # stripe_id is set, so saving does not create a new price in Stripe
            price, created = SubscriptionPrice.objects.get_or_create(
                stripe_id=price_data['stripe_id'],
                defaults={
                    'subscription': plan,
                    'interval': price_data['interval'],
                    'price': Decimal(price_data['price']),
                    'featured': True,
                },
            )
            self.stdout.write(f"  {price.price}/{price.interval}: {'created' if created else 'already exists'}")
