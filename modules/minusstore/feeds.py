# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from minusstore.models import MinusRecord

class LatestArivals(Feed):
    title = "Останні надходження на minus.lviv.ua "
    link = "/"
    description = "Файли, нещодавно завантажені на сайт"

    def items(self):
        return MinusRecord.objects.order_by('-pub_date')[:100]

    def item_pubdate(self, item):
        return item.pub_date



