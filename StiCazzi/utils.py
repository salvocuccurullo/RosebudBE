"""
    iCarusi BE utilities
"""

import json
import decimal
import hashlib
from StiCazzi.models import Notification

def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except:
        return "cannot retrieve ip address"

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

def send_notification(type, title, message, username, image_url='', platform='mobile'):
    notification = Notification(
        type=type, \
        title=title, \
        message=message, \
        platform=platform, \
        image_url=image_url, \
        username=username)
    notification.save()
