"""A simple example of connecting to Earth Engine using App Engine."""



# Works in the local development environment and when deployed.
# If successful, shows a single web page with the SRTM DEM
# displayed in a Google Map.  See accompanying README file for
# instructions on how to set up authentication.

import os
import cgi
import config
import ee
import jinja2
import webapp2

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):                             # pylint: disable=g-bad-name
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        mapid = ee.Image('srtm90_v4').getMapId({'min': 0, 'max': 1000})

        # These could be put directly into template.render, but it
        # helps make the script more readable to pull them out here, especially
        # if this is expanded to include more variables.
        template_values = {
            'mapid': mapid['mapid'],
            'token': mapid['token']
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        factor = float(cgi.escape(self.request.get('factor')))
        m_img = ee.Image('srtm90_v4').polynomial([0,factor])
        mapid = m_img.getMapId({'min': 0, 'max': 1000})

        # These could be put directly into template.render, but it
        # helps make the script more readable to pull them out here, especially
        # if this is expanded to include more variables.
        template_values = {
            'mapid': mapid['mapid'],
            'token': mapid['token']
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
