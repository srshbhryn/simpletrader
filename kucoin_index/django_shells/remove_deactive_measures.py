

def main():
    from django_celery_beat.models import IntervalSchedule, PeriodicTask

    from kucoin_index.config import Type, periods_map, params_map, related_ids_map
    from kucoin_index.models import Measure, Measurement
    measures = Measure.objects.all()
    indices = []
    for type in Type:
        for period in periods_map[type]:
            for params in params_map[type]:
                for related_id in related_ids_map[type]:
                    indices.append({
                        'type': type,
                        'period': period,
                        'related_id': related_id,
                        'params': params,
                    })
    for measure in measures:
        m_dict = {
            'type': measure.type,
            'period': measure.period,
            'related_id': measure.related_id,
            'params': measure.params,
        }
        if not m_dict in indices:
            measure.delete()
main()