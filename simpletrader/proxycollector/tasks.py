
import logging

from celery import shared_task

from simpletrader.proxycollector.models import Proxy
from simpletrader.proxycollector.utils import ProxyHealthCheck

log = logging.getLogger('django')


@shared_task(name='proxycollector.update_proxies_is_active', ignore_result=True, store_errors_even_if_ignored=True)
def update_proxies_is_active():
    for proxy in Proxy.objects.get_deactivated_proxies():
        health_check = ProxyHealthCheck(proxy.ip, proxy.port, proxy.protocol)
        proxy.protocol = health_check.is_active()
