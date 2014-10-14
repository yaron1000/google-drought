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
import gridmet_anomaly
import date_utils, form_utils
#media url containing js/css/img
#Note: needs to be added to app.yaml
MEDIA_URL = 'media/'


#Note appengine uses djang 0.96
#that does not support dict.items call in template
#This is a fx I found online
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def fix_path():
    sys.path.append('my-python-lib')

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
    def get(self):
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)

        '''Set default start and end date'''
        start_date = date_utils.set_back_date(296)
        end_date = date_utils.set_back_date(296 - 7)
        start_dt = date_utils.date_to_datetime(start_date)
        end_dt = date_utils.date_to_datetime(end_date)
        #start_dt = dt.datetime(2013, 12, 15)
        #end_dt = dt.datetime(2013, 12, 31)
        index_image = gridmet_anomaly.ppt_anomaly_func(start_dt, end_dt)

        ## Set color scheme before returning
        mapid = index_image.getMapId({'min':-2.0, 'max':2.0, 'palette':"0000FF,FFFFFF,FF0000"})
        # These could be put directly into template.render, but it
        # helps make the script more readable to pull them out here, especially
        # if this is expanded to include more variables.

        template_values = {
                'MEDIA_URL':MEDIA_URL,
                'mapid': mapid['mapid'],
                'token': mapid['token'],
                'start_date':start_date,
                'end_date':end_date

        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        form_fields = self.request.arguments()
        form_dict={}
        for form_field in form_fields:
            form_dict[form_field] = self.request.get(form_field)
        #form_dict = dict((x,y) for x,y in self.request.get.arguments())
        '''Get start/end dates from user'''
        start_date = cgi.escape(form_dict['start_date'])
        end_date = cgi.escape(form_dict['end_date'])
        #Check that user dataes are valid
        form_fields_to_check = ['start_date', 'end_date']
        form_errors = check_form(form_dict,form_fields_to_check)
        if form_errors:
            template_values = {
                'start_date':start_date,
                'end_date':end_date,
                'form_errors':form_errors
            }
            if 'start_date' in form_errors.keys() and form_errors['start_date']:
                template_values['form_error_start_date'] = form_errors['start_date']
            if 'end_date' in form_errors.keys() and form_errors['end_date']:
                template_values['form_error_end_date'] = form_errors['end_date']
        else:
            start_dt = date_utils.date_to_datetime(start_date)
            end_dt = date_utils.date_to_datetime(end_date)

            index_image = gridmet_anomaly.ppt_anomaly_func(start_dt, end_dt)

            ## Set color scheme before returning
            mapid = index_image.getMapId({'min':-2.0, 'max':2.0, 'palette':"0000FF,FFFFFF,FF0000"})
            # These could be put directly into template.render, but it
            # helps make the script more readable to pull them out here, especially
            # if this is expanded to include more variables.

            template_values = {
                'mapid': mapid['mapid'],
                'token': mapid['token'],
                'start_date':start_date,
                'end_date':end_date

            }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))
#NOTE:
fix_path()
app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
