import os, time, logging, datetime

from django.conf import settings
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
        self.serializers = {}

        for field in self.Meta.model._meta.fields:
            if field.name == 'id':
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
        self.FILE_ROTATE_PERIOD = self.Meta.__dict__.get(
            'rotate_period', settings.JOURNALS.get('ROTATE_PERIOD', 120)
        )
        self.BASE_DIR = settings.JOURNALS.get('DATA_DIR', '/var/simpletrader/journals/')
        self.BASE_DIR = str(self.BASE_DIR)
        self.BASE_DIR += '' if self.BASE_DIR[-1]=='/' else '/'

        self.foreign_key_set = [
            field.name + '_id'
            for field in self.Meta.model._meta.fields
            if type(field) == fields.related.ForeignKey
        ]
        self.sort_field = 'time'
        self.template = self._DELIMITER.join(['{'+key+'}' for key in self.FIELDS]) + '\n'
        self.filename_tamplate = self.BASE_DIR + self.FILE_NAME + '__{time}.csv'
        self._current_fp = None
        self._current_fp_open_time = None
        self._current_fp = open(
            self.filename_tamplate.format(time=self._current_file_time),
            'a',
        )
        self._current_fp_open_time = self._current_file_time

    def _open_new_file(self):
        self._current_fp.close()
        self._current_fp = open(
            self.filename_tamplate.format(time=self._current_file_time),
            'a',
        )
        self._current_fp_open_time = self._current_file_time

    @property
    def _is_current_file_expired(self):
        return not self._current_fp_open_time == self._current_file_time

    @property
    def _current_file_time(self):
        return int(
                time.time()/self.FILE_ROTATE_PERIOD
            )*self.FILE_ROTATE_PERIOD

    @property
    def _current_file(self):
        if self._is_current_file_expired:
            self._open_new_file()
        return self._current_fp

    def append_line(self, obj):
        self._current_fp.write(self.template.format(**obj))

    def _get_obj_from_line(self, line):
        return {
            key: value if not key in self.serializers.keys() else self.serializers[key](value)
            for key, value in zip(
                self.FIELDS,
                line[:-1].split(self._DELIMITER)
            )
        }

    def _bulk_create_file(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        try:
            self.MODEL.objects.bulk_create([
                self.MODEL(**self._get_obj_from_line(line))
                for line in lines
            ])
            return True
        except Exception as e:
            log.warning(f'bulk_create failed. file {filepath}, error: {e}')
            return False

    def _remove_file(self, filepath):
        os.system(f'rm {filepath}')

    def _get_old_files(self):
        old_files = [
            os.path.join(self.BASE_DIR,file)
            for file in os.listdir(self.BASE_DIR)
            if (
                os.path.isfile(
                    os.path.join(self.BASE_DIR, file)
                ) and
                '__' in file and
                self.FILE_NAME in file.split('__')[0] and
                int(
                    file.split('__')[1].split('.csv')[0]
                ) < self._current_file_time
            )
        ]
        old_files.sort()
        # current file and one file before it will always
        # be availabe for trading purposes:
        return old_files[:-1]

    def bulk_create_old_files(self):
        old_files = self._get_old_files()
        fk_key_objs_map = {}
        for filepath in old_files:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            for line in lines:
                obj = self._get_obj_from_line(line)
                fk_key = tuple([
                    obj.get(key) for key in self.foreign_key_set
                ])
                if not fk_key in fk_key_objs_map.keys():
                    fk_key_objs_map[fk_key] = []
                fk_key_objs_map[fk_key].append(obj)

        # sort
        for _, fk_sets_objs in fk_key_objs_map.items():
            fk_sets_objs.sort(key=lambda x: x[self.sort_field])

        # remove duplicate and old entries
        db_max_times = self.MODEL.objects.values(
            *self.foreign_key_set
        ).annotate(max_time=Max(self.sort_field))
        fk_set_to_max_time_map = {}
        for db_max_time in db_max_times:
            fk_key = {k: v for k, v in db_max_time.items()}
            del fk_key['max_time']
            fk_set_to_max_time_map[tuple([
                fk_key.get(k)
                for k in self.foreign_key_set
            ])] = db_max_time['max_time']

        for fk_key, fk_sets_objs in fk_key_objs_map.items():
            seen = set()
            new_l = []
            for d in fk_sets_objs:
                if d[self.sort_field] <= fk_set_to_max_time_map.get(
                    fk_key, unix_timestamp_ms_to_datetime(0)):
                    continue
                t = tuple(d.items())
                if t not in seen:
                    seen.add(t)
                    new_l.append(d)
            fk_key_objs_map[fk_key] = new_l

        got_warning = False
        for fk_key, fk_sets_objs in fk_key_objs_map.items():
            try:
                self.MODEL.objects.bulk_create([
                    self.MODEL(**obj)
                    for obj in fk_sets_objs
                ])
            except Exception as e:
                got_warning = True
                log.warning(f'journal: Failed to bulk_create: error: {e}, model: {self.MODEL.db_table}')
        if got_warning:
            return

        for file in old_files:
            self._remove_file(file)
