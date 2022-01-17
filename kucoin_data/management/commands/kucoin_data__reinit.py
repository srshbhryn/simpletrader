from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from kucoin_data.models import Asset


class Command(BaseCommand):

    def handle(self, *args, **options):
        self._reinit_assets()

    def _reinit_assets(self):
        self.stdout.write('Reinitings assets...')
        for spot_name, futures_name in settings.KUCOIN['ASSETS']:
            _, is_created = Asset.objects.get_or_create(
                spot_name=spot_name,
                futures_name=futures_name,
            )
            if is_created:
                self.stdout.write(f'Asset\'{spot_name}\'|\'{futures_name}\' added.')
            else:
                self.stdout.write(f'Asset\'{spot_name}\'|\'{futures_name}\' already exists.')
        self.stdout.write('Reinitings assets: DONE')
