from typing import Any
from django.core.management import BaseCommand

from subscriptions import utils as subs_utils

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        subs_utils.sync_subs_group_permissions()