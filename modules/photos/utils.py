# -*- coding: utf-8 -*-

from datetime import datetime


def image_upload_filename(instance, filename):
    """
    Generates filenames for uploaded images
    """
    prefix = 'photos'
    uhash = abs(hash(u'%s%s' % (datetime.now(), filename)))
    user = instance.album.user.username
    return u'%s/%s/%s_%s' % (prefix, user, uhash, filename)


def image_optimize(file, width, height, force=False, resize=False):
    """
    Rescales a given image.
    """
    import Image as pil
      
    max_width = width
    max_height = height

    img = pil.open(file)
    
    #Fixing problem with gif
    if img.mode != "RGB":
        img = img.convert("RGB")

    src_width, src_height = img.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = max_width, max_height
    dst_ratio = float(dst_width) / float(dst_height)
    
    if not force:
        if src_height > src_width:
            max_width = dst_height
            max_height = dst_width
        img.thumbnail((max_width, max_height), pil.ANTIALIAS)
    else:
        if dst_ratio < src_ratio:
            crop_height = src_height                   
            crop_width = crop_height * dst_ratio 
            x_offset = int((src_width - crop_width)/2)  
            y_offset = 0 
        else:                                          
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = int((src_height - crop_height)/3)
        img = img.crop((x_offset, y_offset, x_offset+int(crop_width),
                        y_offset+int(crop_height)))
        img = img.resize((dst_width, dst_height), pil.ANTIALIAS)
                
    return img
