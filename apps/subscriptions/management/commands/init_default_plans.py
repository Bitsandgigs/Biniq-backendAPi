from django.core.management.base import BaseCommand
from apps.subscriptions.models import Plan


DEFAULT_PLANS = [
    {"type": "reseller", "tier": "tier1", "amount": 10, "duration": 30},
    {"type": "reseller", "tier": "tier2", "amount": 20, "duration": 90},
    {"type": "reseller", "tier": "tier3", "amount": 30, "duration": 180},
    {"type": "store_owner", "tier": "tier1", "amount": 10, "duration": 30},
    {"type": "store_owner", "tier": "tier2", "amount": 20, "duration": 90},
    {"type": "store_owner", "tier": "tier3", "amount": 30, "duration": 180},
]


class Command(BaseCommand):
    help = 'Initialize default subscription plans if they do not exist'

    def handle(self, *args, **options):
        created_count = 0
        for plan in DEFAULT_PLANS:
            obj, created = Plan.objects.get_or_create(type=plan['type'], tier=plan['tier'], defaults={
                'amount': plan['amount'], 'duration': plan['duration'],
            })
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created plan {obj}"))
        if created_count == 0:
            self.stdout.write(self.style.WARNING('No plans created; all defaults already exist.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Initialized {created_count} plan(s).'))
