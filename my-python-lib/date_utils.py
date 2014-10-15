#!/opt/local/bin/python
import datetime
import re

def set_back_date(days_back):
    '''
    Calculates today - days_back
    and returns the back date in format
    yyyymmdd
    '''
    try:
        int(days_back)
    except:
        return '99990101'
    tdy = datetime.datetime.today()
    #Choose default start_date 4 weeks back
    b = datetime.datetime.today() - datetime.timedelta(days=int(days_back))
    yr_b = str(b.year);mon_b = str(b.month);day_b = str(b.day)
    if len(mon_b) == 1:mon_b = '0%s' % mon_b
    if len(day_b) == 1:day_b = '0%s' % day_b
    back_date = '%s-%s-%s' % (yr_b, mon_b, day_b)
    return back_date

def date_to_datetime(date_str):
    '''
    Function to convert acis date_str of forms
    yyyy-mm-dd
    yyyy/mm/dd
    yyyy:mm:dd
    yyyymmdd
    to datetime. The datetime object is returned
    '''
    eight_date = date_str.replace('-','').replace('/','').replace(':','')
    date_re = re.compile('(\d{4})(\d{2})(\d{2})$')
    try:
        return datetime.datetime(*map(int, date_re.match(eight_date).groups()))
    except AttributeError:
        return None

def datetime_to_date(dt, separator):
    '''
    yyyy-mm-dd
    yyyy/mm/dd
    yyyy:mm:dd
    yyyymmdd
    '''
    try:
        return dt.strftime('%Y{0}%m{0}%d'.format(separator))
    except AttributeError:
        return '0000{0}00{0}00'.format(separator)
