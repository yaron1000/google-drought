"""A simple example of connecting to Earth Engine using App Engine."""

# Works in the local development environment and when deployed.
# If successful, shows a single web page with the SRTM DEM
# displayed in a Google Map.  See accompanying README file for
# instructions on how to set up authentication.

import os
import cgi
import config
import datetime
import time
import ee
import jinja2
import webapp2
import numpy


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):                             # pylint: disable=g-bad-name
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        # mapid = ee.Image('srtm90_v4').getMapId({'min': 0, 'max': 1000})
        self.response.out.write("""<html>
  <head>
    <title>NDVI Temporal Average</title>
    <script type="text/javascript" 
            src="http://maps.google.com/maps/api/js?sensor=false"></script>
    <script type="text/javascript" 
            src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <style>
      body, html
            {width: 100%;height: 100%;}
            body{margin: 0;}
    </style>
  </head>
  <body>
    <script type="text/javascript">
      /**
      * This page will be called from a Python script in App Engine that uses
      * Jinja templates to pass information from the script to the web page.
      * Here we get the mapid and token for the map tiles that were generated
      * by Earth Engine using the Python script ee_appengine.py.
      */

      var MAPID = "{{ mapid }}";
      var TOKEN = "{{ token }}";

      /**
      * The Google Maps API calls getTileUrl when it tries to display a maps
      * tile.  This is a good place to swap in the mapid and token we got from
      * the Python script. The other values describe other properties of the
      * custom map type.
      */
      var eeMapOptions = {
        getTileUrl: function(tile, zoom) {
          var url = ['https://earthengine.googleapis.com/map',
                     MAPID, zoom, tile.x, tile.y].join("/");
          url += '?token=' + TOKEN
          return url;
        },
        tileSize: new google.maps.Size(256, 256)
      };

      // Create the map type.
      var mapType = new google.maps.ImageMapType(eeMapOptions);

       // jQuery detects this state of readiness for you. Code included inside $( document ).ready() will only run once the page Document Object Model (DOM) is ready for JavaScript code to execute.       
      $(document).ready(function () {
        var city = new google.maps.LatLng(39.5272,-119.8219);
        var mapOptions = { zoom:8,center: city, mapTypeId: google.maps.MapTypeId.ROADMAP, clickable:true}
        map = new google.maps.Map($('#map').get(0), mapOptions)
        map.overlayMapTypes.push(null); // create empty overlay entry
        map.overlayMapTypes.setAt("0",mapType);
  
        var marker = new google.maps.Marker({position:new google.maps.LatLng(39.5272,-119.8219), map: map, draggable: true});

        google.maps.event.addListener(marker, 'dragend', function(a) {
          var div = document.createElement('div');
          var longitude=a.latLng.lng().toFixed(4) 
          var latitude=a.latLng.lat().toFixed(4)     
          document.getElementById('UserLatLong').value = longitude+','+latitude;
        });
      })

      google.maps.event.addDomListener(window, 'load', initialize);
    </script>
    <script src="//code.jquery.com/jquery-1.10.2.js"></script>
    <script src="//code.jquery.com/ui/1.11.0/jquery-ui.js"></script>
<!--     
    <div id="toolbar" style="float: left; width: 430px;">
      <h2><center>Multiply SRTM by 2</center></h2>
    </div>

    <div style="margin-left; 430px;">
    </div> -->

    <!-- ANDY's OLD HTML CODE  -->
    <!-- <div id="map" style="width: 640px; height: 480px;"></div>
    <b><p><label for="from">Enter Multiplication Factor</label></b>
    <input type="text" id="from"  value="3" name="MultFactor">  
    <p><div><input type="submit" value="Run-EEFlux"></div> -->

    <table cellpadding="20px">
    <!-- LEFT SIDE OF THE PAGE -->
    <td valign="top" width="30%">
      <h2>NDVI Calculation for Lat Lon point</h2>

      <form action="#" method="post">
          <div>
              <p>
                  <!-- <label for="fac">Factor</label>
                  <input type="text" value="1" name="factor">
                  <br> -->
                  <label for="from">Start Date</label>
                  <input type="text" id="from" value="2013-04-01" name="startdate">
                  <br>
                  <label for="to">End Date</label>
                  <input type="text" id="to" value="2013-07-01" name="enddate">
                  <br>
                  <label for="from">Lon, Lat</label>
                  <input id="UserLatLong" name="UserLatLong" value="-119.8219,39.5272" />
                  <p>
                    <b>Pressing "Run NDVI" computes mean, median, max, and, min NDVI for Longitude/Latitude coordinate</b>
                  <p>
                    <input type="submit" value="Run NDVI">
                    
    </td>

    <!-- RIGHT SIDE OF THE PAGE -->
    <td valign="top" width="70%">
      <div id="map" style="width: 1280px; height: 600px;"></div>
    </td>
    </table>
      
  </body>
</html>
            """)

        # These could be put directly into template.render, but it
        # helps make the script more readable to pull them out here, especially
        # if this is expanded to include more variables.
        # template_values = {
        #     'mapid': mapid['mapid'],
        #     'token': mapid['token']
        # }
        # template = jinja_environment.get_template('index.html')
        # self.response.out.write(template.render(template_values))

        #### A function to compute NDVI for a Landsat image.

    def post(self):
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        
        #### Grabs data from "name" in the HTML form tags
        # factor = float(cgi.escape(self.request.get('factor')))
        startdate = cgi.escape(self.request.get('startdate'))
        enddate = cgi.escape(self.request.get('enddate'))
        UserLatLong = cgi.escape(self.request.get('UserLatLong'))
        UserLatLongX = UserLatLong.split(",")
        UserLong = float(UserLatLongX[0])
        UserLat = float(UserLatLongX[1])

        #### Function to calc NDVI using .map method
        point = ee.Feature.Point(UserLong,UserLat);
        def ndvi_calc_L5L7(refl_toa): 
            ndvi_img = refl_toa.select("B4", "B3").normalizedDifference().select([0],['NDVI'])
            return ee.Image(ndvi_img.copyProperties(refl_toa,['system:index','system:time_start','system_time_end']))

        def ndvi_calc_L8(refl_toa): 
            ndvi_img = refl_toa.select("B5", "B4").normalizedDifference().select([0],['NDVI'])
            return ee.Image(ndvi_img.copyProperties(refl_toa,['system:index','system:time_start','system_time_end']))

        #### MERGE COLLECTIONS FOR TIME PERIOD AND LAT/LON POINT
        l5_coll = ee.ImageCollection('LT5_L1T_TOA').filterBounds(point).filterDate(startdate, enddate);
        l5_coll_ndvi = l5_coll.map(ndvi_calc_L5L7)
        l7_coll = ee.ImageCollection('LE7_L1T_TOA').filterBounds(point).filterDate(startdate, enddate);
        l7_coll_ndvi = l7_coll.map(ndvi_calc_L5L7)
        l8_coll = ee.ImageCollection('LC8_L1T_TOA').filterBounds(point).filterDate(startdate, enddate);
        l8_coll_ndvi = l8_coll.map(ndvi_calc_L8)

        #### Merge NDVI image collections 
        image_coll_ndvi_mrg_L5L7 = ee.ImageCollection(l5_coll_ndvi.merge(l7_coll_ndvi));
        image_coll_ndvi_mrg_L5L7L8 = ee.ImageCollection(image_coll_ndvi_mrg_L5L7.merge(l8_coll_ndvi));

        #### Data in list format
        extract = image_coll_ndvi_mrg_L5L7L8.getRegion(point,1).getInfo();
        extract.pop(0) #remove first row of list ["id","longitude","latitude","time","NDVI"]
        # extractslice = [arr[i][0:2] for i in range(0,2)]
        # extract = list(zip(*extract)[4])
        # for sublist in extract:
            # del sublist[3]
        time_list = [row[3] for row in extract]
        ndvilist = [row[4] for row in extract]        
        # time_list = [datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y,%m,%d") for x in time_list]
        temp_arr = zip(time_list,ndvilist)
        newarray=[['Dates','NDVI']]
        for x in temp_arr:
            if x[1] is not None:
                newarray.append([x[0],x[1]])

        #### CREATE TIME SERIES ARRAY WITH DATE IN COL 1 AND VALUE IN COL 2
        TimeSeries_array = []
        for i in range(0,len(extract),1):
            time_ms = (ee.Algorithms.Date(extract[i][3])).getInfo()['value']
            # data11 = data1['value']
            data1 = time.strftime('%m/%d/%Y',  time.gmtime(time_ms/1000))
            print data1
            data2 = (extract[i][4])
            print data2
            if data2 is not None:
                TimeSeries_array.append([data1,data2])

        #### SORT IN CHRONOLOGICAL ORDER
        TimeSeries_array.sort(key=lambda date: datetime.datetime.strptime(date[0], "%m/%d/%Y"))
        
        #### ADD HEADER TO SORTED LIST 
        TimeSeries_array = [['Dates','NDVI']] + TimeSeries_array

        #### FILTER OUT "None" VALUES
        ndvilist_filt = [x for x in ndvilist if x is not None] 

        #### CALCULATE NDVI STATS 
        meanNDVI = numpy.mean(ndvilist_filt,axis=0)
        medianNDVI = numpy.median(ndvilist_filt,axis=0)
        maxNDVI = numpy.max(ndvilist_filt,axis=0)
        minNDVI = numpy.min(ndvilist_filt,axis=0)
        # These could be put directly into template.render, but it
        # helps make the script more readable to pull them out here, especially
        # if this is expanded to include more variables.

        #### COLOR MAP SPECTRUM
        viz_params = {
            'min':0,
            'max':0.4, 
            'palette':"000000,7F0000,FF0000,FFA500,F5F5DC,D2B38C,40E0D0,7FFF00,006400,0000FF,FF00FF"
        }

        #### GRAB MAPPING PARAMETER TO USE IN TEMPLATE VALUES
        mapid = image_coll_ndvi_mrg_L5L7L8.median().getMapId(viz_params)
        template_values = {
            # 'mapid': mapid['mapid'],
            # 'token': mapid['token'],
            # 'ndvilist_filt': ndvilist_filt,
            'meanNDVIvalue': meanNDVI,
            'medianNDVIvalue': medianNDVI,
            'maxNDVIvalue': maxNDVI,
            'minNDVIvalue': minNDVI,
            'mapid': mapid['mapid'],
            'token': mapid['token'],
            'TimeSeries_array': TimeSeries_array
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))





app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
