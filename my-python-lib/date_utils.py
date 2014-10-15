#!/opt/local/bin/python
import datetime
import re

def set_back_date(days_back=28):
    '''
    Calculates today - days_back
    and returns the back date in format yyyymmdd
    Default is 4 weeks (28 days) back
    '''
    try:
        back_dt = datetime.datetime.today() - datetime.timedelta(days=int(days_back))
        return back_dt.strftime('%Y%m%d')
    except ValueError:
        return '99990101'

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
