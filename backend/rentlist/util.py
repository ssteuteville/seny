import requests
from django.db import models
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from rentlist.models import *
# DISTANCE_SELECT = "POW((lon - %f),2) + POW((lat - %f),2)"
# helpers
DISTANCE_SELECT = "(3959 * acos (cos ( radians(%f) )* cos( radians( lat ) )* cos( radians( lon ) - radians(%f) )+ sin ( radians(%f) )* sin( radians( lat ) )))"

def get_geo(zip_code):
    data = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=%s' % zip_code) # todo: stop using anonymous auth
    data = data.json()['results'][0]['geometry']['location'] # todo add error handling
    return data['lat'], data['lng']


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


def getRecurrenceDates(request):
    options = getRecurrenceOptions(request.POST)
    duration = options['duration']
    metric = options['duration_metric']
    del options['duration']
    del options['duration_metric']
    if metric == 'day':
        dates = [(rec if options.get('byhour', False) else rec.date(), rec + relativedelta(days=+duration)) for rec in rrule(**options)]
        pass
    elif metric == 'week':
        dates = [(rec if options.get('byhour', False) else rec.date(), rec + relativedelta(weeks=+duration)) for rec in rrule(**options)]
    else:
        dates = [(rec if options.get('byhour', False) else rec.date(), rec + relativedelta(months=+duration)) for rec in rrule(**options)]

    return dates


def getRecurrenceOptions(data):
    ret = dict()
    weekdays = {'mo': MO, 'tu': TU, 'we': WE, 'th': TH, 'fr': FR, 'sa': SA, 'su': SU }
    frequencies = {'daily': DAILY, 'weekly': WEEKLY, 'monthly': MONTHLY, 'hourly': HOURLY}
    if data.get('byhour', None):
        ret['byhour'] = (int(hour) for hour in data.get('byhour', None).split(','))
    if data.get('interval', None):
        ret['interval'] = int(data.get('interval', None))
    if data.get('freq', None):
        ret['freq'] = frequencies[data.get('freq', None)]
    if data.get('byweekday', None):
        ret['byweekday'] = (weekdays[day] for day in data.get('byweekday', None).split(','))
    if data.get('bymonthday', None):
        ret['bymonthday'] = (int(day) for day in data.get('bymonthday', None).split(','))
    if data.get('bymonth', None):
        ret['bymonth'] = data.get('bymonth', None)
    if data.get('dtstart', None):
        ret['dtstart'] = parse(data['dtstart'], fuzzy=True).date()
    if data.get('until'):
        ret['until'] = parse(data['until'], fuzzy=True).date()
    ret['duration'] = int(data.get('duration', 1))
    ret['duration_metric'] = data.get('duration_metric', "day")
    return ret