"""A simple example of connecting to Earth Engine using App Engine."""

# Works in the local development environment and when deployed.
# If successful, shows a single web page with the SRTM DEM
# displayed in a Google Map.  See accompanying README file for
# instructions on how to set up authentication.


import datetime as dt
import os, sys
import config
import ee
import jinja2
import webapp2
import cgi

#Custom modules
'''
from my_python_lib import date_utils
from my_python_lib import form_utils
from my_python_lib import gridmet_anomaly
'''
#import matplotlib
import gridmet_anomaly
import date_utils, form_utils, graph_utils
#media url containing js/css/img
#Note: needs to be added to app.yaml
MEDIA_URL = 'media/'
#increase timeout

from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def fix_path():
    sys.path.append('/Users/bdaudert/my-python-lib')

def check_form(form, fields_to_check):
    '''
    '''
    form_errors = {}
    for field in fields_to_check:
        checker = getattr(form_utils, 'check_' + field)
        err = checker(form)
        if err:
            form_errors[field] = err
    return form_errors


class MainPage(webapp2.RequestHandler):

    def get_palette(self):
        #palette = '0000FF,00FF00,FFFF00,FF0000' #Blue/Green/Yellow/Red
        #palette = 'FF0000,FFFF00,00FF00,0000FF' #Red/Yellow/Green/Blue
        palette= '67001F,B2182B,D6604D,F4A582,FDDBC7,F7F7F7,D1E5F0,92C5DE,4393C3,2166AC,053061' #Charles palette
        return palette

    def get_start_end_date(self):
        start_date = self.request.get('start_date',None)
        end_date = self.request.get('end_date',None)
        #Format to 8 digit string
        if start_date:
            start_date = start_date.replace('/','').replace('-','').replace(':','')
        if end_date:
            end_date = end_date.replace('/','').replace('-','').replace(':','')
        return start_date, end_date

    def get_reducer_args(self, reduce_type):
        wusa = [[-125,24],[-125,50],[-66,24],[-66, 50]]
        #wusa = [[-125,24],[-125,25],[-124,24],[-124, 25]]
        reduce_args = {
            'bestEffort': True,
            'geometry': ee.Feature.Polygon(wusa),
            'scale':4000
        }
        if reduce_type == 'max':
            reduce_args['reducer'] = ee.Reducer.max()
        else:
            reduce_args['reducer'] = ee.Reducer.min()
        return reduce_args
    '''
    def get_reducer_args(self,reduce_type):
        wusa = [[-125,24],[-125,50],[-66,24],[-66, 50]]
        #wusa = [[-125,24],[-125,25],[-124,24],[-124, 25]]
        reduce_args = {
            'bestEffort': False,
            'geometry': ee.Feature.Polygon(wusa),
            'maxPixels':50000000,
            'scale':4000
        }
        if reduce_type == 'max':
            reduce_args['reducer'] = ee.Reducer.max()
        else:
            reduce_args['reducer'] = ee.Reducer.min()
        return reduce_args
    '''
    def get_init_template_values(self, MEDIA_URL, palette):
        template_values = {
            'MEDIA_URL': MEDIA_URL,
            'run_error': '',
            'mapid': {},
            'token':{},
            'max':-9999.0,
            'min':9999.0,
            'palette':palette,
        }
        return template_values

    def get(self):
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        template = jinja_environment.get_template('index.html')
        palette = self.get_palette()
        template_values = self.get_init_template_values(MEDIA_URL, palette)
        '''Set default start and end date'''
        start_date, end_date = self.get_start_end_date()
        if not start_date or not end_date:
            #Initial page without url parameters
            start_date = date_utils.set_back_date(14)
            end_date = date_utils.set_back_date(7)
        else:
            #Request parameters submitted via url string
            collection = gridmet_anomaly.ppt_anomaly_func(start_date, end_date)
            #template_values['collection'] = collection
            #Find max/min over all pixels for map legend generation
            reduce_args_mx = self.get_reducer_args('max')
            mn = 0
            mx = 200
            mx = collection.reduceRegion(**reduce_args_mx).getInfo()['pr']
            reduce_args_mn = self.get_reducer_args('min')
            #reduce_args['reducer'] = ee.Reducer.min()
            mn = collection.reduceRegion(**reduce_args_mn).getInfo()['pr']
            template_values['max'] = mx
            template_values['min'] = mn
        template_values['start_date'] = start_date
        template_values['end_date'] = end_date
        mapid = None
        try:
            mapid = collection.getMapId({'min':mn, 'max':mx, 'palette':palette})
        except Exception, e:
            try:
                mapid = collection.getMapId({'min':mn, 'max':mx, 'palette':palette})
            except:
                template_values['run_error'] = str(e)
                #self.response.out.write(template.render(template_values))

        if mapid:
            template_values['mapid'] = mapid['mapid']
            template_values['token'] = mapid['token']
        self.response.out.write(template.render(template_values))

    def post(self):
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        template = jinja_environment.get_template('index.html')
        palette = self.get_palette()
        template_values = self.get_init_template_values(MEDIA_URL, palette)
        form_fields = self.request.arguments()
        form_dict={}
        for form_field in form_fields:
            form_dict[form_field] = self.request.get(form_field)
        #form_dict = dict((x,y) for x,y in self.request.get.arguments())
        '''Get start/end dates from user'''
        start_date, end_date = self.get_start_end_date()
        template_values['start_date'] = start_date
        template_values['end_date'] = end_date
        #Check that user dataes are valid
        form_fields_to_check = ['start_date', 'end_date']
        form_errors = check_form(form_dict,form_fields_to_check)
        if form_errors:
            template_values['form_errors'] = form_errors
            if 'start_date' in form_errors.keys() and form_errors['start_date']:
                template_values['form_error_start_date'] = form_errors['start_date']
            if 'end_date' in form_errors.keys() and form_errors['end_date']:
                template_values['form_error_end_date'] = form_errors['end_date']
        else:
            collection = gridmet_anomaly.ppt_anomaly_func(start_date, end_date)
            template_values['collection'] = collection
            mx = 200
            #Find max/min over all pixels for map legend generation
            reduce_args_mx = self.get_reducer_args('max')
            mx = collection.reduceRegion(**reduce_args_mx).getInfo()['pr']
            reduce_args_mn = self.get_reducer_args('min')
            mn = collection.reduceRegion(**reduce_args_mn).getInfo()['pr']
            template_values['max'] = mx
            template_values['min'] = mn
            ## Set color scheme before returning
            mapid = None
            try:
                mapid = collection.getMapId({'min':mn, 'max':mx, 'palette':palette})
            except Exception, e:
                try:
                    mapid = collection.getMapId({'min':mn, 'max':mx, 'palette':palette})
                except:
                    template_values['run_error'] = str(e)
                    self.response.out.write(template.render(template_values))
        if mapid:
            template_values['mapid'] = mapid['mapid']
            template_values['token'] = mapid['token']
        self.response.out.write(template.render(template_values))
#NOTE:
fix_path()
app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
