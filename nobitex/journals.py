import os, time, logging

from django.conf import settings

from .models import MarketData, MarketTrades


log = logging.getLogger('binance')


class JournalManger:
    _DELIMITER = ','

    def __init__(
        self,
        MODEL,
        FIELDS,
        FILE_NAME,
        FILE_ROTATE_PRERIOD, ## in seconds.
        BASE_DIR,
    ):
        self.MODEL = MODEL
        self.FIELDS = FIELDS
        self.FILE_NAME = FILE_NAME
        self.FILE_ROTATE_PRERIOD = FILE_ROTATE_PRERIOD
        self.BASE_DIR = str(BASE_DIR)
        self.BASE_DIR += '' if self.BASE_DIR[-1]=='/' else '/'
        if '__' in self.FILE_NAME:
            raise ValueError('FILE_NAME cant contain "__".')
        if '__' in self.BASE_DIR:
            raise ValueError('BASE_DIR cant contain "__".')

        self.template = self._DELIMITER.join(['{'+key+'}' for key in self.FIELDS]) + '\n'
        self.filename_tamplate = self.BASE_DIR + self.FILE_NAME + '__{time}.csv'

    @property
    def _current_file_time(self):
        return int(
                time.time()/self.FILE_ROTATE_PRERIOD
            )*self.FILE_ROTATE_PRERIOD

    @property
    def _currnet_file(self):
        return self.filename_tamplate.format(
            time=self._current_file_time
        )


    def append_line(self, obj):
        with open(self._currnet_file, 'a') as f:
            f.write(self.template.format(**obj))

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
            log.warning(f'bluk_create failed. file {filepath}, error: {e}')
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
        ].reverse()
        # current file and one file before it will always
        # be availabe for trading purposes:
        return old_files[:-1]

    def bulk_create_old_files(self):
        for filepath in self._get_old_files():
            if self._bulk_create_file(filepath):
                self._remove_file(filepath)


marketdata_journal = JournalManger(
    MODEL=MarketData,
    FIELDS=[
        'market_id',
        'price',
        'volume',
        'is_buy',
        'time',
    ],
    FILE_NAME='marketdata',
    FILE_ROTATE_PRERIOD=settings.NOBITEX[
        'JOURNAL_ROTATE_PERIOD'
    ][
        'marketdata_journal'
    ],
    BASE_DIR=settings.NOBITEX['DATA_DIR_PATH'],
)

trade_journal = JournalManger(
    MODEL=MarketTrades,
    FIELDS=[
        'market_id',
        'time',
        'price',
        'volume',
        'is_buy',
    ],
    FILE_NAME='trades',
    FILE_ROTATE_PRERIOD=settings.NOBITEX[
        'JOURNAL_ROTATE_PERIOD'
    ][
        'trade_journal'
    ],
    BASE_DIR=settings.NOBITEX['DATA_DIR_PATH'],
)