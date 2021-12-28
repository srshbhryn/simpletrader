import os, time, logging

from django.conf import settings
from django.db.models.fields.related import ForeignKey

log = logging('django')

class JournalManger:
    _DELIMITER = ','

    def __init__(self    ):
        self.MODEL = self.Meta.model
        self.FIELDS = [
            field.name + '_id' if type(field) == ForeignKey else field.name
            for field in self.Meta.model._meta.fields
        ]
        self.FILE_NAME = self.MODEL._meta.db_table
        self.FILE_ROTATE_PERIOD = self.Meta.__dict__.get(
            'rotate_period', settings.JOURNALS.get('ROTATE_PERIOD', 120)
        )
        self.BASE_DIR = settings.JOURNALS.get('DATA_DIR', '/var/simpletrader/journals/')
        self.BASE_DIR += '' if self.BASE_DIR[-1]=='/' else '/'

        self.template = self._DELIMITER.join(['{'+key+'}' for key in self.FIELDS]) + '\n'
        self.filename_tamplate = self.BASE_DIR + self.FILE_NAME + '__{time}.csv'
        self._current_fp = None
        self._current_fp_open_time = None
        self._current_fp = open(self._current_file, 'a')
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
            key: value
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
        for filepath in self._get_old_files():
            if self._bulk_create_file(filepath):
                self._remove_file(filepath)
