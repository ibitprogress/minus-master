# -*- coding: utf-8 -*-
import time
import pytils
from django.conf import settings 
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import os.path

def up_filename(instance, filename):
    """
    generate filename to upload
    it consists of user-id/sha-hash/original-filename
    """
    from models import MinusPlusRecord
    if isinstance(instance, MinusPlusRecord):
        prefix = u'pluses'
    else:
        prefix = u'files'
    label = u'user/%d' % instance.user.pk
    basename,extension = os.path.splitext(filename.split('/')[-1])
    filename = pytils.translit.slugify(basename)+extension #make safe filename
    hashd = abs(hash(u'%s%s' % (time.time(), filename))) #generate unique hash
    return u'%s/%s/%s/%s' % (prefix,label, hashd, filename)  

audio_storage = FileSystemStorage(location=settings.STORAGE_ROOT)

def allowed_extensions():
    """Generate list of allowed extensions, for flash-uploader"""
    from minusstore.models import FileType #somehow, cant import globally
    exts=""
    for ft in FileType.objects.all():
        for ext in ft.filetype.split(','):
            exts+="*."+ext+";"
    return exts
