import calendar
import date_utils
import datetime

today = datetime.datetime.today()
yesterday = date_utils.date_to_datetime(date_utils.set_back_date(1))

def check_start_date(form):
    err = None
    date = form['start_date'].replace('-','').replace('/','').replace(':','')
    e_date = form['end_date'].replace('-','').replace('/','').replace(':','')
    if len(date)!=8:
        return '%s is not a valid date.' %form['start_date']
    try:
        int(date)
    except:
        return '%s is not a valid date.' %form['start_date']

    #Check month
    if int(date[4:6]) < 1 or int(date[4:6]) > 12:
        return 'Not a valid month.'
    #Check day
    if int(date[6:8]) < 1 or int(date[4:6]) > 31:
        return 'Not a valid day.'


    #Check for leap year issue
    if not calendar.isleap(int(date[0:4])) and date[4:6] == '02' and date[6:8] == '29':
        return '%s is not a leap year. Change start date to February 28.' %date[0:4]

    #Check that start date is earlier than end date
    try:
        sd = datetime.datetime(int(date[0:4]), int(date[4:6].lstrip('0')), int(date[6:8].lstrip('0')))
    except:
        return err
    try:
        ed = datetime.datetime(int(e_date[0:4]), int(e_date[4:6].lstrip('0')), int(e_date[6:8].lstrip('0')))
    except:
        return err
    if ed < sd:
        return 'Start Date is later then End Year.'

    if sd > yesterday:
        return 'Start Date should be no later than yesterday.'
    return err

def check_end_date(form):
    err = None
    date = form['end_date'].replace('-','').replace('/','').replace(':','')
    s_date = form['start_date'].replace('-','').replace('/','').replace(':','')
    if len(date)!=8:
        return '%s is not a valid date.' %form['end_date']
    try:
        int(date)
    except:
        return '%s is not a valid date.' %form['end_date']

    #Check month
    if int(date[4:6]) < 1 or int(date[4:6]) > 12:
        return 'Not a valid month.'
    #Check day
    if int(date[6:8]) < 1 or int(date[4:6]) > 31:
        return 'Not a valid day.'


    #Check for leap year issue
    if not calendar.isleap(int(date[0:4])) and date[4:6] == '02' and date[6:8] == '29':
        return '%s is not a leap year. Change start date to February 28.' %date[0:4]

    #Check that start date is earlier than end date
    try:
        ed = datetime.datetime(int(date[0:4]), int(date[4:6].lstrip('0')), int(date[6:8].lstrip('0')))
    except:
        return err
    try:
        sd = datetime.datetime(int(s_date[0:4]), int(s_date[4:6].lstrip('0')), int(s_date[6:8].lstrip('0')))
    except:
        return err
    '''
    if ed < sd:
        return 'Start Date is later then End Date.'
    '''
    if ed > today:
        return 'End Date is later than today.'
    return err
