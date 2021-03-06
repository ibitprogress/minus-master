from django.core.urlresolvers import reverse
import datetime
import calendar
from django.utils.datastructures import SortedDict

import locale
locale.setlocale(locale.LC_ALL, ("uk_UA", "UTF8"))
from calendar import HTMLCalendar, Calendar
from django import template

from minusstore.models import MinusRecord

register = template.Library()

@register.simple_tag
def gencal(obj_list, year=None, month=None, calendar_class=None):
    """
    Renders a simple calendar of the given month and year if none are
    specified. Accomplishes this by passing the arguments to
    :class:`ListCalendar`

    ::

      {% gencal queryset %}

      {% gencal queryset 1983 12 %}
      

    :param obj_list: A list of objects to render on the calendar.
    :type obj_list: list.
    :keyword year: Year to render.
    :type year: int.
    :keyword month: Month to render.
    :type month: int.
    :returns: calendar as HTML
    :rtype: str.
    """
    today = datetime.date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month
    if not calendar_class:
        calendar_class = ListCalendar
    return ''.join(calendar_class(obj_list).formatmonth(year, month))

class ListCalendar(HTMLCalendar):
    """
    This is a calendar object which accepts a ``list`` argument and a
    ``date_field`` keyword argument.. This class will return an HTML
    calendar with links on the days that are present in the list,
    using ``date_field`` as the lookup.

    It's assumed that the provided list is valid for the given month,
    ie: contains no outside dates.

    Usage::

        >>> from datetime import datetime, timedelta
        >>> from gencal.templatetags.gencal import ListCalendar
        >>> subclass = type('SubListClass', (ListCalendar,),{}) # This is equivalent to a subclass
        >>> subclass.get_link(self, dt) = lambda dt: "/items/%d/%d/%d" % (dt.year, dt.month, dt.day)
        >>> dates = [{'date':datetime.now(), 'name':'test'},
        ... {'date':datetime.now() + timedelta(days=5), 'name':'test2'}]
        >>> lc = subclass(dates)
        >>> print "".join(lc.formatmonth(2009, 01))
        <table border="0" cellpadding="0" cellspacing="0" class="month">
        <tr><th colspan="7" class="month">January 2009</th></tr>
        <tr><th class="mon">Mon</th><th class="tue">Tue</th><th class="wed">Wed</th><th class="thu">Thu</th><th class="fri">Fri</th><th class="sat">Sat</th><th class="sun">Sun</th></tr>
        <tr><td><a href="/items/2008/12/29">29</a></td><td><a href="/items/2008/12/30">30</a></td><td><a href="/items/2008/12/31">31</a></td><td><a href="/items/2009/1/1">1</a></td><td><a href="/items/2009/1/2">2</a></td><td><a href="/items/2009/1/3">3</a></td><td><a href="/items/2009/1/4">4</a></td></tr>
        <tr><td><a href="/items/2009/1/5">5</a></td><td><a href="/items/2009/1/6">6</a></td><td><a href="/items/2009/1/7">7</a></td><td><a href="/items/2009/1/8">8</a></td><td><a href="/items/2009/1/9">9</a></td><td><a href="/items/2009/1/10">10</a></td><td><a href="/items/2009/1/11">11</a></td></tr>
        <tr><td><a href="/items/2009/1/12">12</a></td><td><a href="/items/2009/1/13">13</a></td><td><a href="/items/2009/1/14">14</a></td><td><a href="/items/2009/1/15">15</a></td><td><a href="/items/2009/1/16">16</a></td><td><a href="/items/2009/1/17">17</a></td><td><a href="/items/2009/1/18">18</a></td></tr>
        <tr><td><a href="/items/2009/1/19">19</a></td><td><a href="/items/2009/1/20">20</a></td><td><a href="/items/2009/1/21">21</a></td><td><a href="/items/2009/1/22">22</a></td><td><a href="/items/2009/1/23">23</a></td><td><a href="/items/2009/1/24">24</a></td><td><a href="/items/2009/1/25">25</a></td></tr>
        <tr><td><a href="/items/2009/1/26">26</a></td><td><a href="/items/2009/1/27">27</a></td><td><a href="/items/2009/1/28">28</a></td><td><a href="/items/2009/1/29">29</a></td><td><a href="/items/2009/1/30">30</a></td><td><a href="/items/2009/1/31">31</a></td><td><a href="/items/2009/2/1">1</a></td></tr>
        </table>

    :param cal_items: A list of items to put in the calendar.
    :type cal_items: list.
    :keyword year: Year to render.
    :type year: int.
    :keyword month: Month to render.
    :type month: int.
    """

    def __init__(self, cal_items, year=None, month=None, *args, **kwargs):
        today = datetime.date.today()


        if year == None:
            year = today.year
        self.year = year

        if not month:
            month = today.month
        self.month = month

        self.date_field = 'pub_date'

        super(ListCalendar, self).__init__(*args, **kwargs)

        cal_arr = self.monthdatescalendar(year, month)
        month_dict = SortedDict()
        for week in cal_arr:
            for date in week:
                month_dict[date] = []

        for item in cal_items:
            if isinstance(item, dict):
                possible_date = item.get(self.date_field)
            else:
                possible_date = getattr(item, self.date_field)
            if type(possible_date) == datetime.datetime:
                # transform possible_date to a date, not a datetime
                possible_date = possible_date.date()
            if possible_date:
                month_dict[possible_date].append(item)
        self.month_dict = month_dict

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.

        :arg day: A day to be formatted.
        :type day: date object.
        :arg weekday: Weekday of given day.
        :type weekday: int.
        """
        link = self.get_link(day)
        code = '<td%s>%s</td>'
        attr = ''
        url = day.day
        if link:
            # return link
            url = '<a href="%s">%s</a>' % (link,  day.day)
        if day == datetime.datetime.now().date():
            attr = ' class="today" '
        return code % (attr, url)

    def get_link(self, dt):
        """
        Should return a url to a given date, as represented by ``dt``
        
        :arg dt: date to turn into a url
        :type dt: date/datetime
        """
        dt = datetime.datetime(dt.year, dt.month, dt.day)
        if dt in MinusRecord.objects.dates('pub_date', 'day'):
            return reverse('minus_archive_day',args=[dt.year, dt.month, dt.day])
        else:
            return None

    def monthdates2calendar(self, year, month):
        """
        Function returns a list containing a list of tuples
        (representing a week), the tuples represent a
        ``datetime.date`` for the given day and the weekday associated
        with it.

        This is something that ought to be implemented in core. We
        have monthdatescalendar, monthdayscalendar,
        monthdays2calendar, but no monthdates2calendar.

        :keyword year: Year to render.
        :type year: int.
        :keyword month: Month to render.
        :type month: int.
        :returns: Tuple of (datetime, weekday).
        :rtype: tuple(datetime, int)
        """
        return [[(dt, dt.weekday()) for dt in week] for week in self.monthdatescalendar(year, month)]

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (calendar.month_name[themonth], theyear)
        else:
            s = '%s' % calendar.month_name[themonth]
        url = reverse('minus_archive_month', args = [theyear, themonth])
        return '<tr><th colspan="7" class="month"><a href="%s">%s</a></th></tr>' % (url, s)

    def formatmonth(self, theyear, themonth, withyear=False):
        """
        Return a formatted month as a table.

        Overridden so weeks will use monthdates2calendar, so we have
        access to full date objects, rather than numbers.

        :arg theyear: Year of calendar to render.
        :type theyear: int.
        :arg themonth: Month of calendar to render
        :type themonth: int.
        :keyword withyear: If true, it will show the year in the header.
        :type withyear: bool.
        """
        v = []
        a = v.append
 
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdates2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return v
