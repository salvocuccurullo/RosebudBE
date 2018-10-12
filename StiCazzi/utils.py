"""
    iCarusi BE utilities
"""

import json
import decimal
import hashlib


def decimal_dumps(dec):

    """ Convert decimal to string """

    def fix_dict(dec):
        """ Fix Dict """
        fixed = {}
        for k, value in dec.items():
            if isinstance(value, decimal.Decimal):
                # convert decimal to string
                fixed.update({k: str(value)})
            elif isinstance(value, dict):
                # recurse
                fixed.update({k: fix_dict(value)})
            else:
                # no conversion needed, replace
                fixed.update({k: value})
        return fixed
    return json.dumps(fix_dict(dec))


def safe_file_name(name, file_type):

    """ Convert file name to sha1 """

    name = str(name).encode('utf-8')
    file_type = str(file_type)
    ext = "xxx"

    try:
        ext = file_type.split("/")[1]
    except IndexError:
        ext = "xxx"

    final_fname = hashlib.sha1(name).hexdigest()
    final_fname += "." + ext

    return final_fname
