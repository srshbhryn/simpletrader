import datetime
import uuid
import re
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP

from django.db.models import QuerySet


def convert(word, convert_to_camelcase=False):
    if not convert_to_camelcase:
        return word
    if not isinstance(word, str):
        return word
    return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), word)



def normalize_number(num):
    if not isinstance(num, (int, float, Decimal)):
        return str(num)
    if isinstance(num, float):
        num = Decimal(str(num))
    str_value = f'{num:f}'
    if '.' in str_value:
        str_value = str_value.rstrip('0').rstrip('.')
    return str_value


def serialize_decimal(obj, opts=None):
    return str(obj)

def serialize(obj, opts=None, ignore_keys=None, convert_to_camelcase=False):
    """ Serializes an object, optimized for the project data model

        Levels:
          * 0: minimal output, for large lists
          * 1: only direct fields are returned
          * 2: only non-expensive joins/operations
          * 3: some computationally expensive operations
    """
    if ignore_keys is None:
        ignore_keys = []
    opts = opts or {}
    level = opts.get('level', 1)
    if obj is None:
        return None
    if isinstance(obj, (uuid.UUID)):
        return obj.hex
    if isinstance(obj, (int, float, str, bool)):
        return obj
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.timestamp()
    if isinstance(obj, (datetime.datetime, datetime.timedelta)):
        return obj.total_seconds()
    if isinstance(obj, (list, QuerySet)):
        return [serialize(x, opts=opts, ignore_keys=ignore_keys, convert_to_camelcase=convert_to_camelcase) for x in obj]
    if isinstance(obj, dict):
        return {convert(k, convert_to_camelcase): serialize(v, opts=opts, ignore_keys=ignore_keys, convert_to_camelcase=convert_to_camelcase) for k, v in obj.items() if k not in ignore_keys}
    if isinstance(obj, Decimal):
        return serialize_decimal(obj, opts=opts)

    data = {}
    # model_serialize = BaseSerializer.serialize(obj, opts=opts)
    # if model_serialize is not None:
    #     data = model_serialize
    return serialize(data, opts=opts, ignore_keys=ignore_keys, convert_to_camelcase=convert_to_camelcase)


def serialize_choices(choices, obj, opts=None):
    """ Return the identifier code name of the given value of a Choices field
    """
    if not hasattr(choices, '_serialize_map'):
        choices._serialize_map = {db_value: identifier for identifier, db_value in choices._identifier_map.items()}
    return choices._serialize_map.get(obj, None)


def serialize_dict_key_choices(choices, obj, opts=None):
    """ Convert dictionary keys from Choices field values to identifier code names

    To keep value keys in response, set `merge` option.
    """
    serialized_dict = {serialize_choices(choices, key): value for key, value in obj.items()}
    if opts and opts.get('merge'):
        serialized_dict.update(obj)
    return serialized_dict


def serialize_currency(obj, opts=None):
    return serialize_choices(Currencies, obj, opts=opts)


def serialize_timestamp(obj, opts=None):
    return int(obj.timestamp() * 1000)
