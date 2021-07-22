from django.contrib import admin

from .models import Market, MarketTrades, MarketData

admin.site.register(Market)
admin.site.register(MarketTrades)
admin.site.register(MarketData)
