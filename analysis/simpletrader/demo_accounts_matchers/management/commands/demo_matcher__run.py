
from django.core.management.base import BaseCommand
from simpletrader.demo_accounts_matchers.nobitex import NobitexDemoMatcher

class Command(BaseCommand):
    def handle(self, *args, **options):
        mathcer = NobitexDemoMatcher()
        mathcer.run()

