from typing import Any
from django.core.management import BaseCommand

from subscriptions import utils as subs_utils

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-dangling',
            action='store_true',
            default=False,
        )
    
    def handle(self, *args: Any, **options: Any):
        # python manage.py sync_user_subs --clear-dangling
        clear_dangling = options.get('clear_dangling')
        if clear_dangling:
            print('Clearing dangling not in user active subs in stripe')
            subs_utils.clear_dangling_subs() # clear all not active subs in stripe
        else:
            print('Sync active subs')
            done = subs_utils.refresh_active_users_subscriptions(active_only=True, verbose=True)
            if done:
                print('Done')