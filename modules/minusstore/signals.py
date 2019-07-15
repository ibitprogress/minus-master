# -*- coding: utf-8 -*-
import subprocess, os
import datetime
import shutil
from django.db.models import signals
from dateutil.relativedelta import relativedelta
from django.contrib.comments.models import Comment
from models import MinusRecord, MinusPlusRecord, MinusCategory, MinusAuthor, CommentNotify


def timed_arivals(period="day"):
    "returns latest minuses for specified amount of time"
    today = datetime.datetime.now().date()
    td = relativedelta
    if period == "day":
        shift = td(days=1 )
    elif period == "week":
        shift = td(weeks=1) 
    elif period == "two_weeks":
        shift = td(weeks=2) 
    elif period == "month":
        shift = td(months=1)
    fdate = today - shift
    return MinusRecord.objects.filter(pub_date__gte = fdate)


def relations(sender, signal, instance, created = False,  *args, **kwargs):
    """
    Manage non-direct relations between objects in db.
    add instance's filetype to author's list of types,
    and cleanup empty items after editing or deleting

    here goes some ugly code
    """
    plus =  MinusPlusRecord.objects.filter(minus = None,
        user = instance.user)
    
    
    if plus and not signal == signals.post_delete:
        try:
            instance.up_plusrecord.delete() #remove old plus
        except MinusPlusRecord.DoesNotExist:
            pass
        item = plus[0]
        item.minus = instance
        item.save()
        if plus.count() > 1: #trash from previous not-ended uploads
            for p in plus[1:]:
                p.delete()

    if not created and instance.author:
        #cleanup empty authors categories and types
        
        if len(MinusRecord.objects.filter(author = instance.author,\
        type = instance.type)) == 0:
            instance.author.filetypes.remove(instance.type)
        authors_to_delete = MinusAuthor.objects.filter(records_by = None)
        # if we posibly have a collision and can delete
        # author that was created right now and have no reccords attached
        # so, we delete older author, with lesser id
        if authors_to_delete.count() == 1\
        and authors_to_delete[0].id != MinusAuthor.objects.all()[:1][0].id\
        or signal == signals.post_delete:
            authors_to_delete.delete()
        elif authors_to_delete.count() > 1:
            authors_to_delete.order_by('id')[0].delete()
        MinusCategory.objects.filter(records_in_category = None).delete()
    elif instance.author:
        instance.author.filetypes.add(instance.type)
    else:
        # in case of emergency. It should not happen, but suddenly happens
        instance.author,created = MinusAuthor.objects.get_or_create(name = u"Невідомий виконавець")


def comments_glue(sender, signal, instance, created = False, *args, **kwargs):
    """Create notification about unread comments"""
    if created and instance:
        obj = instance.content_object
        if not instance.user == obj.user:
            notify = CommentNotify.objects.create(comment = instance,
                object_id = instance.object_pk,
                content_type = instance.content_type,
                user = obj.user)


def rm_comment_notifications(sender, signal, instance, created = False, *args, **kwargs):
    if instance.is_removed:
        try:
            CommentNotify.objects.get(comment = instance).delete()
        except:
            pass

def recode_plus(sender,signal,instance, created = False, *args, **kwargs):
    if created:
        filename = instance.file.path
        tmpname = filename + ".orig.mp3" #preserve original file
        shutil.move(filename, tmpname)
        #and then convert
        sp = subprocess.Popen("lame -m mono\
            --tt \"minus.lviv.ua\"\
            --preset cbr 48 \"%s\"  \"%s\" " % \
            (tmpname, filename),
            shell = True, env = {'PATH': str(os.getenv('PATH'))},
            stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)


def merge_authors(sender,signal,instance,*args,**kwargs):
    """
    when authors get renamed from admin interface, two authors with same names
    should be merged into one
    """
    qs = MinusAuthor.objects.filter(name = instance.name)
    if qs.count() > 1:
        for author in qs[1:]:
            author.records_by.update(author = qs[0])
            author.delete()

signals.post_save.connect(recode_plus, sender = MinusPlusRecord)
signals.post_save.connect(relations, sender = MinusRecord)
signals.post_delete.connect(relations, sender = MinusRecord)
signals.post_save.connect(comments_glue, sender = Comment)
signals.post_save.connect(rm_comment_notifications, sender = Comment)
signals.post_save.connect(merge_authors, sender = MinusAuthor)
