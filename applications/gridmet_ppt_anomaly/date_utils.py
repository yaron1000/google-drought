#!/opt/local/bin/python
import datetime

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
    if len(eight_date) != 8:
        return None
    dt = datetime.datetime(int(eight_date[0:4]),int(eight_date[4:6]), int(eight_date[6:8]))
    return dt

def datetime_to_date(dt, seperator):
    '''
    yyyy-mm-dd
    yyyy/mm/dd
    yyyy:mm:dd
    yyyymmdd
    '''
    if type(dt) != datetime.datetime:
        return '0000' + str(seperator) + '00' + str(seperator) + '00'
    try:y = str(dt.year)
    except:y = '0000'
    try:
        m =str(dt.month)
        if len(m) ==1:m = '0' + m
    except:
        m = '00'
    try:
        d =str(dt.day)
        if len(d) ==1:d = '0' + m
    except:
        d = '00'
    return y + str(seperator) + m + str(seperator) + d
