import os, uuid, logging

from django.conf import settings
from django.core.cache import cache
from django.db.models import fields
from django.db.models import Max

from timescale.db.models.fields import TimescaleDateTimeField

from base.utils import unix_timestamp_ms_to_datetime

log = logging.getLogger('journal')


class Journal:
    _DELIMITER = ','

    def __init__(self):
        self.MODEL = self.Meta.model
        self.FIELDS = [
            field.name + '_id' if type(field) == fields.related.ForeignKey else field.name
            for field in self.Meta.model._meta.fields
            if not field.name == 'id'
        ]
        self.sort_field = self.Meta.__dict__.get('sort_field', 'sort_field')
        self.FIELDS.append(self.sort_field)
        self.serializers = {
            fieldname: func
            for fieldname, func in self.Meta.__dict__.get('serializers', {}).items()
        }
        self.serializers[self.sort_field] = int
        for field in self.Meta.model._meta.fields:
            if field.name == 'id':
                continue
            if field.name in self.serializers.keys():
                continue
            if type(field) == fields.related.ForeignKey:
                self.serializers[field.name + '_id'] = int
            else:
                for type_, serializer in [
                    (TimescaleDateTimeField,
                        lambda value: unix_timestamp_ms_to_datetime(int(value))),
                    (fields.IntegerField, int),
                    (fields.FloatField, float),
                    (fields.BooleanField, lambda value: value == 'True'),
                ]:
                    if type(field) == type_:
                        self.serializers[field.name] = serializer

        self.FILE_NAME = self.MODEL._meta.db_table
        self.BASE_DIR = settings.JOURNALS.get('DATA_DIR', '/var/simpletrader/journals/')
        self.BASE_DIR = str(self.BASE_DIR)
        self.BASE_DIR += '' if self.BASE_DIR[-1]=='/' else '/'

        self.foreign_key_set = [
            field.name + '_id'
            for field in self.Meta.model._meta.fields
            if type(field) == fields.related.ForeignKey
        ]
        self.template = self._DELIMITER.join(['{'+key+'}' for key in self.FIELDS]) + '\n'
        self.filename = self.BASE_DIR + self.FILE_NAME + '.csv'
        self._last_sequence_cache_key = 'journal:' + self.filename + ':ltsq'
        self._db_insert_lock_key = 'journals:' + self.filename + ':lock'
        self.fp = open(
            self.filename,
            'a',
        )

    def foreign_keys_key_from_obj(self, obj):
        foreign_key_values = [
            obj[key]
            for key in self.foreign_key_set
        ]
        return tuple(foreign_key_values)

    def get_last_sequences(self):
        return cache.get(self._last_sequence_cache_key) or {}

    def set_last_sequence(self, values):
        return cache.set(self._last_sequence_cache_key, values)

    def __del__(self):
        self.fp.close()

    def append_line(self, obj):
        self.fp.write(self.template.format(**obj))

    def _get_obj_from_line(self, line):
        return {
            key: value if not key in self.serializers.keys() else self.serializers[key](value)
            for key, value in zip(
                self.FIELDS,
                line[:-1].split(self._DELIMITER)
            )
        }

    def _bulk_create(self):
        number_of_lines = int(os.popen(f'cat {self.filename} | wc -l').read()[:-1])
        with open(self.filename, 'r') as f:
            lines = [
                f.readline()
                for _ in range(number_of_lines)
            ]
        last_sequences = self.get_last_sequences()
        fk_to_new_sequences = {}
        new_objects = []
        for line in lines:
            obj = self._get_obj_from_line(line)
            fk_key = self.foreign_keys_key_from_obj(obj)
            sort_field = obj[self.sort_field]
            del obj[self.sort_field]
            if last_sequences.get(fk_key, -1) > sort_field:
                continue
            if sort_field in fk_to_new_sequences.get(fk_key, set()):
                continue
            new_objects.append(obj)
            if not fk_key in fk_to_new_sequences.keys():
                fk_to_new_sequences[fk_key] = set()
            fk_to_new_sequences[fk_key].add(sort_field)

        self.MODEL.objects.bulk_create([
            self.MODEL(**obj)
            for obj in new_objects
        ])
        for k, v in fk_to_new_sequences.items():
            last_sequences[k] = max(v)
        self.set_last_sequence(last_sequences)
        os.system(f'sed -i \'1,{number_of_lines}d\' {self.filename}')

    def _lock(self):
        uid = str(uuid.uuid4())
        return cache.get_or_set(self._db_insert_lock_key, uid) == uid

    def _unlock(self):
        cache.delete(self._db_insert_lock_key)

    def insert_to_db(self):
        if not self._lock():
            return
        try:
            self._bulk_create()
        except Exception as e:
            self._unlock()
            log.error(f'journal: insert db failed: error: {e}.')
            raise e
        self._unlock()
