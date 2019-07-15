import datetime
from django.forms.extras.widgets import SelectDateWidget

class LegacySelectDateWidget(SelectDateWidget):
    """
    Legacy widget from SelectDateWidget
    """

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year-90, this_year)[::-1] # Show years from bigger
