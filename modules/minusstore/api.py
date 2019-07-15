from tastypie import fields
from tastypie.resources import ModelResource, Resource
from models import MinusRecord, MinusAuthor, FileType, MinusWeekStats
from django.contrib.auth.models import User
from haystack.query import SearchQuerySet


class ShortedModelResource(ModelResource):


    def _dehydrate_short(self, bundle):
        """change in subclass"""
        return bundle

    def _dehydrate_full(self, bundle):
        """change in subclass"""
        return bundle

    def _switch(self, request):
        """ugly hook to switch dehydration methods"""
        if request.GET.has_key('full') and request.GET['full'] == 'true':
            self.dehydrate = self._dehydrate_full
        else:
            self.dehydrate = self._dehydrate_short
        
    # patch methods to switch dehydration methods
    def dispatch(self, request_type, request, **kwargs):
        self._switch(request)
        return super(ModelResource, self).dispatch(request_type, request, **kwargs)

    def get_multiple(self, request, **kwargs):
        self._switch(request)
        return super(ModelResource, self).get_multiple(request, **kwargs)

class MinusAuthorResouce(ShortedModelResource):
    records = fields.ToManyField('minusstore.api.MinusRecordResource', 'records_by')
    class Meta:
        resource_name = 'minusauthor' #same automatically
        queryset = MinusAuthor.objects.all()
        allowed_methods = ['get']
        filtering = {
            "name": ('exact', 'startswith',),
        }
        ordering = ['name']
        
    def _dehydrate_short(self, bundle):
        """change in subclass"""
        bd = {'id':bundle.data['id'],
            'name':bundle.data['name'],
            'resource_uri':bundle.data['resource_uri']
        }
        return bd

class FileTypeResource(ModelResource):
    class Meta:
        resource_name = 'minusfiletype'
        queryset = FileType.objects.all()
        allowed_methods = ['get']


class MinusRecordResource(ShortedModelResource):
    author = fields.ForeignKey(MinusAuthorResouce, 'author')
    filetype = fields.ForeignKey(FileTypeResource, 'type', full= True)
    class Meta:
        queryset = MinusRecord.objects.all()
        resource_name = 'minusrecord' #same automatically
        allowed_methods = ['get']
        #fields = ['title']
        filtering = {
            "title": ('exact', 'startswith',),
            "lyrics": ('lt','gt',),
            "filetype": ('exact','in'),
        }
        ordering = ["pub_date","rating_score"]


    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(MinusRecordResource, self).build_filters(filters)

        if "q" in filters:
            sqs = SearchQuerySet().auto_query(filters['q'])

            orm_filters = {"pk__in" : [i.pk for i in sqs]}

        return orm_filters


    def _dehydrate_short(self, bundle):
        """put foreignkey data into the serialized bundle"""
        bd = {'title':bundle.data['title'],
            'id':bundle.data['id'],
            'resource_uri':bundle.data['resource_uri'],
            'length':bundle.data['length'],
            'filesize':bundle.data['filesize'],
            'file':bundle.data['file']}
        bd['author_name'] = bundle.obj.author.name
        bd['filetype'] = str(bundle.obj.type.id)
        if bundle.obj.lyrics: bd['lyrics'] = 'true'
        else: bd['lyrics'] = 'false'
        bundle.data = bd
        return bundle

    def _dehydrate_full(self, bundle):
        """put foreignkey data into the serialized bundle"""
        #bundle.data['user'] = bundle.obj.user.get_profile().fullname()
        bundle.data['author_name'] = bundle.obj.author.name
        bundle.data['filetype'] = str(bundle.obj.type)
        return bundle

class MinusWeekStatsResource(ShortedModelResource):
    minus = fields.ForeignKey(MinusRecordResource, 'minus')
    class Meta:
        resource_name = 'minusweekstats'
        queryset = MinusWeekStats.objects.filter(rate__gt = 0)
        allowed_methods = ['get']

    def _dehydrate_short(self, bundle):
        """put foreignkey data into the serialized bundle"""
        bd = {'title':bundle.obj.minus.title,
            'id':bundle.obj.minus.id,
            'resource_uri':'/api/v1/minusrecord/%s/' % (bundle.obj.minus.id),
            'length':bundle.obj.minus.length,
            'filesize':bundle.obj.minus.filesize,
            'file':bundle.obj.minus.file.url}
        bd['author_name'] = bundle.obj.minus.author.name
        bd['filetype'] = str(bundle.obj.minus.type.id)
        if bundle.obj.minus.lyrics: bd['lyrics'] = 'true'
        else: bd['lyrics'] = 'false'
        bundle.data = bd
        return bundle

    def _dehydrate_full(self, bundle):
        """put foreignkey data into the serialized bundle"""
        #bundle.data['user'] = bundle.obj.user.get_profile().fullname()
        bundle.data['author_name'] = bundle.obj.author.name
        bundle.data['filetype'] = str(bundle.obj.type)
        return bundle


