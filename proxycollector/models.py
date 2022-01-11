from datetime import timedelta

from django.db import models
from django.utils.timezone import now

from base.models import Country

DEACTIVATED_TIME_TO_REMOVE = timedelta(days=1)

class ProxyManager(models.Manager):
    def remove_old_deactivated_proxies(self):
        self.filter(models.Q(
            models.Q(checked_at__is_null=True) &
            models.Q(last_active_datetime__lte=now()-DEACTIVATED_TIME_TO_REMOVE)
        ) | models.Q(
            models.Q(is_active=False) &
            models.Q(checked_at__gte=models.F('last_active_datetime') + DEACTIVATED_TIME_TO_REMOVE)
        )).delete()

    def get_proxy_for_country(self, country):
        return self.filter(is_active=True, country=country).first()

    def get_deactivated_proxies(self):
        return self.filter(is_active=False)


class Proxy(models.Model):
    class ProtocolChoices(models.IntegerChoices):
        socks5 = 1
        socks4 = 2
        http = 3
        https = 4

    is_active = models.BooleanField(default=False)
    checked_at = models.DateTimeField(null=True, blank=True)
    last_active_datetime = models.DateTimeField(auto_now_add=True)
    country = models.IntegerField(db_index=True, choices=Country.choices, null=True, blank=True)
    is_country_verified = models.BooleanField(default=False)
    ip = models.CharField(max_length=64)
    port = models.CharField(max_length=8)
    protocol = models.IntegerField(choices=ProtocolChoices.choices)

    objects = ProxyManager()

    class Meta:
        unique_together = [
            ['ip', 'port', 'protocol'],
        ]
        indexes = [
            models.Index(
                fields=['country',],
                condition=models.Q(is_active=True),
                name='proxy_index_active_proxies'
            ),
        ]

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def __del__(self):
        if self.is_active:
            self.last_active_datetime = now()
            self.save(update_fields=['last_active_datetime'])
        super().__del__(self)
