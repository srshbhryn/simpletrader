from decimal import Decimal
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import models
from celery import shared_task

from simpletrader.base.db import Round
from simpletrader.base.serializers import serialize

from .models import Trade


@shared_task(name='analysis.q.get_prices_volume')
def get_prices_volume_task(market_id, from_datetime, to_datetime, bucket_size, price_rounding_precision,):
    """query:
        SELECT
            time_bucket(0 :01 :00, "analysis_trade"."time") AS "bucket",
            ROUND(
                (
                    "analysis_trade"."quote_amount" / ("analysis_trade"."base_amount" * 1E + 2)
                )
            ) AS "rounded_price",
            SUM("analysis_trade"."base_amount") AS "total_volume"
        FROM
            "analysis_trade"
        WHERE
            (
                "analysis_trade"."market_id" = 1
                AND "analysis_trade"."time" > 2023 -02 -09 16 :25 :32.074053 + 00 :00
                AND "analysis_trade"."time" < 2023 -02 -09 17 :25 :32.074067 + 00 :00
            )
        GROUP BY
            time_bucket(0 :01 :00, "analysis_trade"."time"),
            ROUND(
                (
                    "analysis_trade"."quote_amount" / ("analysis_trade"."base_amount" * 1E + 2)
                )
            )
        ORDER BY
            "bucket" DESC
    """
    from_datetime = timezone.make_aware(datetime.fromtimestamp(float(from_datetime)))
    to_datetime = timezone.make_aware(datetime.fromtimestamp(float(to_datetime)))
    price_rounding_precision = Decimal(price_rounding_precision).normalize()
    bucket_size = timedelta(seconds=float(bucket_size))
    amounts = Trade.objects.filter(
        market_id=market_id,
        time__gt=from_datetime,
        time__lt=to_datetime,
    ).time_bucket_with_origin('time', bucket_size, timezone.now()).annotate(rounded_price=models.ExpressionWrapper(expression=price_rounding_precision * Round(
        models.F('quote_amount') / (models.F('base_amount') * price_rounding_precision)
    ), output_field=models.FloatField(),)).values('bucket', 'rounded_price').annotate(
        total_volume=models.Sum('base_amount'),
    )
    return serialize(list(amounts))
