import hashlib
import uuid

from django.conf import settings


def to_md5(str):
    h = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    h.update(str.encode(encoding='utf-8'))
    return h.hexdigest()


def uid(string):
    data = "{}-{}".format(str(uuid.uuid4()), string)
    return to_md5(data)
