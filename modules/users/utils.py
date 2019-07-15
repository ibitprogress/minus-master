# -*- coding: utf-8 -*-
import datetime


def avatar_upload_filename(instance, filename):
    """
    Generates filenames for uploaded avatars
    """
    prefix = 'avatars'
    uhash = abs(hash(u'%s%s' % (datetime.datetime.now(), filename)))
    user = instance.user.username
    return u'%s/%s/%s_%s' % (prefix, user, uhash, filename)


def avatar_optimize(file, width, height, force=False):
    """
    Rescales a given avatar image.
    """
    import Image as pil
      
    max_width = width
    max_height = height

    img = pil.open(file)
    
    #Fixing problem with gif
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    if not force:
        img.thumbnail((max_width, max_height), pil.ANTIALIAS)
    else:
        src_width, src_height = img.size
        src_ratio = float(src_width) / float(src_height)
        dst_width, dst_height = max_width, max_height
        dst_ratio = float(dst_width) / float(dst_height)
                
        if dst_ratio < src_ratio:
            crop_height = src_height                    # height is the same
            crop_width = crop_height * dst_ratio # make right wid/heig balance
            x_offset = int((src_width - crop_width)/2) # move offset to the 
            y_offset = 0                               # left, so crop frame
        else:                                          # is now on the mid
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = int((src_height - crop_height)/3)
        img = img.crop((x_offset, y_offset, x_offset+int(crop_width),
                        y_offset+int(crop_height)))
        img = img.resize((dst_width, dst_height), pil.ANTIALIAS)
                
    return img
