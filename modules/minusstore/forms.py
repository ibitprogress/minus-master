# -*- coding: utf-8 -*-
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2,TPE1,TALB,COMM
import datetime
import pytils
import os.path

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.db.models import Count

from haystack.forms import SearchForm
from haystack.query import SearchQuerySet,EmptySearchQuerySet

from minusstore.models import MinusRecord, FileType, MinusAuthor,\
    MinusPlusRecord, MinusCategory,MinusStopWord\
    ,TEMPO_CHOICES,GENDER_CHOICES,STAFF_CHOICES


class BaseMusicForm(forms.ModelForm):
    """abstract form for cleaning mp3-s"""
    def __init__(self, *args, **kwargs):
        self.mp3info = {}
        super(BaseMusicForm, self).__init__(*args, **kwargs)


    def check_max_size(self, cd):
        if cd.has_key('file'):
            from django.conf import settings
            if cd['file'].size > settings.MAX_FILE_SIZE:
                e = forms.ValidationError(mark_safe(\
                u"Розмір файлу повинен не перевищувати: %s , ваш файл: %s"\
                %( str(settings.MAX_FILE_SIZE), cd['file'].size)))
                self._errors['file'] = e.messages
                del cd['file']


    
    def set_fyletype(self, cd, ext):
        try:
            ft = FileType.objects.get(filetype__contains=ext)
            cd['type'] = ft
        except FileType.DoesNotExist:
            e = forms.ValidationError(mark_safe(u"Невідомий тип файлу: "+ ext)) 
            self._errors['file'] = e.messages
            if cd.has_key('file'):
                del cd['file']


    def get_mp3info(self,filename):
        """convert idv3tag to unicode and store into form"""
        self.mp3info = MP3(filename)
        tryencodings = 'cp1251', 'koi8-r', 'cp1252'
        baseenc = 'iso-8859-1'

        for key, value in self.mp3info.items():  #check each item for encoding
            if value.encoding!=3 and\
                isinstance(getattr(value, 'text', [None])[0], unicode):
                if value.encoding == 0:     #if we get wrong enc. (3 = unicode)
                    bytes= '\n'.join(value.text).encode(baseenc)
                    for encoding in tryencodings:
                        try:
                            bytes.decode(encoding)  #we try to decode with
                        except UnicodeError:        #each of ours encs
                            pass
                        else:
                            break
                    else:
                        raise ValueError('None of the tryencodings work for\
                            %r key %r' % (path, key))
                    if type(value.text) == type(list()):  #sometimes we get list
                        for i in range(len(value.text)):  #in tag-data
                            value.text[i]= value.text[i].encode(baseenc).\
                                decode(encoding)
                    else:                   #but sometimes unicode
                        value.text = value.text.encode(baseenc).decode(encoding)

                value.encoding= 3

    
class UploadForm(BaseMusicForm):
    """
    Form with lot's of validation and processing. Upload minuses to site
    for now form has a little inconsistent structure, because of
    evolutionary development
    """
    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput)
    author = forms.CharField(required = False, label = u'Виконавець',
            help_text = "Виконавець оригінального твору")
    type = forms.CharField(required = False, widget = forms.HiddenInput)
    add_category = forms.CharField(required = False, label = '', help_text =\
        u'Або ви можете додати власний жанр, якщо не знайшли його у списку')
    
    def __init__(self, *args, **kwargs):
        if 'edit' in kwargs:
            self.edit = kwargs.pop('edit')
        else:
            self.edit = False

        super(UploadForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MinusRecord

    ### START: Methods that are used in form validation ###


    def check_for_matches(self, cd):
        if cd.has_key('file'):
            matches = MinusRecord.objects.filter(filesize = cd['file'].size)
            if matches: #file name get's slugified
                basename,extension = os.path.splitext(cd['file'].name)
                matches = matches.filter(file__contains = \
                pytils.translit.slugify(basename)+extension)
                if matches:
                    e = forms.ValidationError(mark_safe(\
                    u"Файл вже присутній у базі: ")) 
                    self._errors['file'] = e.messages
                    del cd['file']



    def check_stopwords(self,cd,fieldname):
        """
        function for checking fields for matching with stop-words
        """
        
        for w in cd[fieldname].split():
            qs = MinusStopWord.objects.filter(word = w.lower)
            if qs:
                stopword = qs[0]
                if stopword.blocked:
                    e = forms.ValidationError(mark_safe(u"Недопустиме слово ")) 
                    self._errors[fieldname] = e.messages
                    del cd[fieldname]
                else:
                    cd[fieldname] = cd[fieldname].\
                        lower().\
                        replace(qs[0].word,'').\
                        strip().\
                        title() #title after lowering

    def check_misplaced_name(self, cd):
        """
        Often users misplace song author's name and surname
        so we can automagically place it right
        """
        qs = MinusAuthor.objects
        splitname = cd['author'].split()
        for word in splitname:
            qs = qs.filter(name__icontains = word)
            # name should contain all words in any order
            # but in this case we also get authors with words
            # that are not in our data e.g. : George Michael and Britney Spears,
            # when we was looking only for george Michael
            # so filter it back 
        if qs:
            for author in qs.annotate(num_rec = Count('records_by')).\
                    order_by('-num_rec'):
                for word in author.name.split():
                    if word in splitname: matched = True
                    else: matched = False
                if matched:
                    cd['author'] = author.name
                    break





    def fill_artist_and_title(self, cd, ext):
        if cd.has_key('file'):
            if ext == 'mp3':
                try:
                    self.get_mp3info(cd['file'].file.name)
                except (ValueError, KeyError, AttributeError):
                    pass

            if cd['is_folk']:
                author = u'Народна'
            else:
                author = unicode(cd['author'].strip())
                if author == u'' :
                    if self.mp3info.has_key('TPE1'):
                        author = self.mp3info['TPE1'].text[0]
                        #file can be mp3, but not have tags
                    else:
                        author = u'Невідомий Виконавець'
            cd['author'] = author.title()


            if cd['title'] == '':
                if self.mp3info.has_key('TIT2'):
                    cd['title'] = self.mp3info['TIT2'].text[0]
                else:
                    cd['title'] = cd['file'].name[:-len(ext)-1]
                    # get original filename minus extension, minus dot (.)


            # check for stop_words
            self.check_stopwords(cd,'author')
            self.check_misplaced_name(cd)
            cd['author'], created = MinusAuthor.objects.get_or_create(name = cd['author'])
        
            self.check_stopwords(cd,'title')

    def check_embed(self,cd ):
        if cd['embed_video']:
            code = cd['embed_video']        #here we define type of video
            if code.find('youtube.com') != -1:      #string search!
                cd['embed_video'] = \
                settings.INLINES_START_TAG+\
                " youtube "\
                + code \
                + settings.INLINES_END_TAG      # actually more efficent
                                                # validation goes in
                                                # django_inlines 
                                                # here we just find-out         
                                                # the type of embed
            else:
                e = forms.ValidationError(mark_safe(u"Невірний код вставки ")) 
                self._errors['embed_video'] = e.messages
                del cd['embed_video']

    def add_cats(self,cd):
        if cd['add_category']:
            display_name = cd['add_category'].strip().capitalize()[:14] #maxlen
            name = pytils.translit.slugify(cd['add_category'])[:19] #safe name
            cat,created = MinusCategory.objects.get_or_create(name = name,
                display_name = display_name)
            if self.edit:                               
                self.instance.categories.add(cat)       
                cats = list(self.instance.categories.all())
            else:                                       
                cats = list(cd['categories'])
                cats.append(cat)    
            cd['categories'] = cats     

    def fill_idv3(self,cd):
        """docstring for fill"""
        if self.mp3info:
            self.mp3info.update({
                'TPE1':TPE1(encoding =3, text = [cd['author']]),
                'TIT2':TIT2(encoding =3, text = [cd['title']]),
                'TALB':TALB(encoding =3, text = [u"Записи користувача "+\
                        cd['user'].\
                        get_profile().fullname()]),
                "COMM::'eng'":COMM(encoding=3, lang="eng", desc="",
                    text=[u"downloaded from minus.lviv.ua"]),
                "COMM":COMM(encoding=3, lang="ukr", desc="",
                    text=[u"Звантажено з minus.lviv.ua"])
            })
            self.mp3info.save()

        
        
        
        
    ### END:Methods that are used in form validation ###

    def clean(self):
        self._validate_unique = True
        cd = self.cleaned_data
        if not cd.has_key('file') or cd['file'] == None:
            if self.edit:
                    cd['file'] = self.instance.file
            else:
                e = forms.ValidationError(mark_safe(\
                u"Додайте будьласка файл")) 
                self._errors['file'] = e.messages
                del cd['file']
                return cd

        ext = cd['file'].name.split(".")[-1].lower()

        self.check_max_size(cd)
        self.add_cats(cd)
        if not self.edit:
            self.check_for_matches(cd)
        self.set_fyletype(cd, ext)
        self.fill_artist_and_title(cd, ext)
        self.check_embed(cd)
        self.fill_idv3(cd)
        return cd

    def _post_clean(self):
        """
        if we got some validation errors, eg no atuhor or etc
        we don't need to validate model, because it will fail
        """
        if not self._errors:
            super(UploadForm, self)._post_clean()

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(UploadForm, self).save(commit=False)
        minus = self.instance
        ext = minus.file.name.split(".")[-1].lower()
        #may be it should be enclosed in try-except
        if ext == 'mp3':
            # doing it here because it's not validation, but post-processing and we are
            # dealing with instance instead of cleaned_data

            len = self.mp3info.info.length
            hr = int(len/60/60)
            len %=  60*60
            min =int(len/60)
            sec =int(len%60)
            self.instance.length = datetime.time(hr,min,sec)

            self.instance.bitrate = self.mp3info.info.bitrate/1000

        self.instance.filesize = self.cleaned_data['file'].size

        if commit:
            m.save()
        self.save_m2m()
        return m


defalut_value = (('',"Не важливо"),)
D_TEMPO_CHOICES = defalut_value+TEMPO_CHOICES
D_GENDER_CHOICES = defalut_value+GENDER_CHOICES
D_STAFF_CHOICES = defalut_value+STAFF_CHOICES


class MinusSearchForm(SearchForm):
    q = forms.CharField(label = u"Знайти", required=False, help_text\
        = u"Сюди можна ввести назву, виконавця, або уривок зі слів пісні")
    is_folk = forms.BooleanField(label=u"Народна",required=False)
    is_childish = forms.BooleanField(label=u"Дитяча",required=False)
    is_ritual = forms.BooleanField(label=u"Обрядова",required=False)
    tempo = forms.ChoiceField(label=u"Темп композиції",
        initial=D_TEMPO_CHOICES[0],
        choices = D_TEMPO_CHOICES, required=False)
    gender = forms.ChoiceField(label=u"Стать виконавця",
        initial=D_GENDER_CHOICES[0],choices = D_GENDER_CHOICES, required=False)
    staff = forms.ChoiceField(label=u"Виконавчий склад",
        choices = D_STAFF_CHOICES,
        initial=D_STAFF_CHOICES[0],
        required=False)
    categories = forms.ModelMultipleChoiceField(label = u"Жанри:",
        required = False,
        queryset=MinusCategory.objects.all())
    types = forms.ModelMultipleChoiceField(label = u"Типи файлів:",
        required = False,
        queryset=FileType.objects.all())


    def no_query_found(self):
        return self.searchqueryset.all()

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        if hasattr(self, 'cleaned_data'):
            sqs = super(MinusSearchForm, self).search()
            cd = self.cleaned_data
            if cd['is_folk']:
                sqs = sqs.filter(is_folk = 'True')
            if cd['is_childish']:
                sqs = sqs.filter(is_childish = 'True')
            if cd['is_ritual']:
                sqs = sqs.filter(is_ritual = 'True')
            if cd['gender']:
                sqs = sqs.filter(gender = cd['gender'])
            if cd['tempo']:
                sqs = sqs.filter(tempo = cd['tempo'])
            if cd['staff']:
                sqs = sqs.filter(staff = cd['staff'])
            if cd['types']:
                sqs = sqs.filter(type__in = cd['types'])
            if cd['categories']:
                #do OR-based many-to-many search
                #it has a lot of hacks because of super-strange
                #behaviour when dealing with more than one SearchQuerySet
                csqs = sqs.filter(categories=cd['categories'][0].id)
                #prepopulate query first
                for cat in cd['categories'][1:]: #and iterate then
                    q = sqs.filter(categories=cat.id) 
                    if len(q) > 0:
                        #if we add empty qs then result will be empty %( (bug?)
                        csqs = csqs | q #adding via logical OR
                sqs = csqs.all()
        else: sqs = EmptySearchQuerySet()
                    
        return sqs

class MinusPlusForm(BaseMusicForm):
    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput) 
    class Meta:
        model = MinusPlusRecord
        fields = ('file','user')

    def clean(self):
        cd = self.cleaned_data
        if not cd.has_key('file'):
            e = forms.ValidationError(mark_safe(\
            u"Додайте будь ласка mp3 файл")) 
            self._errors['file'] = e.messages
        else:
            ext = cd['file'].name.split(".")[-1].lower()

            self.check_max_size(cd)
            self.set_fyletype(cd, ext)
        return cd
        
