import datetime
from haystack.indexes import *
from haystack import site
from minusstore.models import MinusRecord


class MinusRecIndex(SearchIndex):
    text = CharField(document = True, default = " ",
        use_template = True)
    title = CharField(model_attr = 'title')
    author = CharField(model_attr='author')
    annotation = CharField(model_attr='annotation')
    type = CharField(model_attr = 'type')
    lyrics = CharField(model_attr='lyrics')
    categories = MultiValueField()
    tempo = CharField(model_attr='tempo')
    staff = CharField(model_attr='staff')
    gender = CharField(model_attr='gender')
    pub_date = DateTimeField(model_attr='pub_date')
    # using CharField instead of BooleanField because
    # of whoosh's weirdness with booleans
    is_folk = CharField(model_attr='is_folk')
    is_childish = CharField(model_attr='is_childish')
    is_ritual = CharField(model_attr='is_ritual')

    def prepare_categories(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        # we can prepare the list here.
        if obj.categories.all():
            return [category.id for category in obj.categories.all()]
        else:
            return [-1]

    def prepare_is_folk(self, obj):
        return str(obj.is_folk)

    def prepare_is_childish(self, obj):
        return str(obj.is_childish)

    def prepare_is_ritual(self, obj):
        return str(obj.is_ritual)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return MinusRecord.objects.filter(pub_date__lte=datetime.datetime.now())

site.register(MinusRecord, MinusRecIndex)



