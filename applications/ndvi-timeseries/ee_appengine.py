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
import time
import sys
import json


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

MAIN_PAGE_HTML = """<html>
  <head>
    <title>Accessing arguments in UI events</title>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <style>
        html, body {
            height: 100%;
            width: 100%;
            margin: 0px;
            padding: 0px
        }

        #map-canvas {
            height:100%;
            width:100%;
            position: relative;
        }

        .button {
            background-color:#F4FA58;
            border:2px solid black;   
        }

        #wrapper {
          height: 100%;
          width: 100%; 
        }

        #menu {
          z-index: 100; 
          position: absolute; 
          margin: 10px 0px 0px 200px;
          background-color: #fff; 
          border: 1px #000 Solid; 
          padding: 5px;
        }

        #chart_div { 
          position: fixed; 
          /*width: 700px;*/
          /*height: 350px;*/
          /*top: 50px; */
          min-width: 50%;
          height: 400px;
          margin: 0 auto;
          /*left: 0;*/
          bottom: 0; 
          right: 0;
          z-index: 99;
          /*border: 1px solid #888;*/
        } 



    </style>

    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp"></script>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <!-- 
    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
 -->
    <script>
    var map;
    function initialize() {

        /**
         * Create new map
         */
        var mapDiv = document.getElementById('map-canvas');
        var mapOptions = {
            zoom: 5,
            center: new google.maps.LatLng(35.8250, -90.5555),
            mapTypeId: 'hybrid',
            draggableCursor: 'pointer'
        };
        map = new google.maps.Map(mapDiv, mapOptions);
        
        /**
         * Global marker object that holds all markers.
         * @type {Object.<string, google.maps.LatLng>} 
         */
        var markers = {};

        /**
        
         * Concatenates given lat and lng with an underscore and returns it.
         * This id will be used as a key of marker to cache the marker in markers object.
         * @param {!number} lat Latitude.
         * @param {!number} lng Longitude.
         * @return {string} Concatenated marker id.
         */
        var getMarkerUniqueId = function (lat, lng) {
            return lat + '_' + lng;
        }

        /**
         * Creates an instance of google.maps.LatLng by given lat and lng values and returns it.
         * This function can be useful for getting new coordinates quickly.
         * @param {!number} lat Latitude.
         * @param {!number} lng Longitude.
         * @return {google.maps.LatLng} An instance of google.maps.LatLng object
         */
        var getLatLng = function (lat, lng) {
            return new google.maps.LatLng(lat, lng);
        };

        /**
         * Binds click event to given map and invokesvar lat_lng;
            a callback that appends a new marker to clicked location.
         */
        var lat,lng,lat_lng_string,v,v_list,lat_lng,new_lat_lng_string;
        var addMarker = google.maps.event.addListener(map, 'click', function (e) {
            lat = e.latLng.lat(); // lat of clicked point
            lng = e.latLng.lng(); // lng of clicked point
            lat_lng_string = (Math.round(lat*1000) / 1000).toString() + ',' + (Math.round(lng*1000) / 1000).toString();
            //Set lat_lng_string hidden var
            v = document.getElementById('lat_lng_string').value;
            if (v != ''){v+=','}
            v+= lat_lng_string;
            document.getElementById('lat_lng_string').value = v;
            var markerId = getMarkerUniqueId(lat, lng); // an that will be used to cache this marker in markers object.
            var marker = new google.maps.Marker({
                position: getLatLng(lat, lng),
                map: map,
                id: 'marker_' + markerId,
                lat_lon_string:lat_lng_string
            });
            //marker.lat_lon_str = lat + ',' + lng;
            markers[markerId] = marker; // cache marker in markers object
            bindMarkerEvents(marker); // bind right click event to marker
            console.log(markers);
       
        });

        /**
         * Binds right click event to given marker and invokes a callback function that will remove the marker from map.
         * @param {!google.maps.Marker} marker A google.maps.Marker instance that the handler will binded.
         */
        var bindMarkerEvents = function (marker) {
            google.maps.event.addListener(marker, "click", function (point) {
                var markerId = getMarkerUniqueId(point.latLng.lat(), point.latLng.lng()); // get marker id by using clicked point's coordinate
                var marker = markers[markerId]; // find marker
                //Remove lat lng from lat_lng_str
                v = document.getElementById('lat_lng_string').value;
                v_list = v.split(',');
                new_lat_lng_string ='';
                for (idx=0;idx< v_list.length - 1;idx+=2){

                    lat_lng = v_list[idx] + ',' + v_list[idx+1];

                    if (marker.lat_lon_string != lat_lng){

                        new_lat_lng_string+=lat_lng + ',';

                    }
                }
                //Remove trailing comma
                new_lat_lng_string = new_lat_lng_string.substring(0,new_lat_lng_string.length - 1);
                document.getElementById('lat_lng_string').value = new_lat_lng_string;
                removeMarker(marker, markerId); // remove it
                console.log(markers);
            });
        };

        /**
         * Removes given marker from map.
         * @param {!google.maps.Marker} marker A google.maps.Marker instance that will be removed.
         * @param {!string} markerId Id of marker.
         */
        var removeMarker = function (marker, markerId) {
            marker.setMap(null); // set markers setMap to null to remove it from map
            delete markers[markerId]; // delete marker instance from markers object
        };
    }

    google.maps.event.addDomListener(window, 'load', initialize);

    initialize();

    </script>

<!-- 
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
          var TimeSeries_array = {{ TimeSeries_array }};
            
          var data = google.visualization.arrayToDataTable(TimeSeries_array);
          
          var options = {
            title: 'NDVI',
            hAxis: {title: 'Dates', titleTextStyle: {color: 'blue'}},
            vAxis: {title: 'NDVI', titleTextStyle: {color: 'blue'}}
          };
          
          
          //var chart = new google.visualization.ColumnChart(document.getElementById('chart_div')));
          //var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
          var chart = new google.visualization.LineChart(document.getElementById('chart_div'));

          chart.draw(data, options);

    }
    </script>
 -->
</head>
  <body>
      <div id="wrapper">
        <div id="menu">
          <p> Click on map to add marker (click again to remove), or manually add Lat,Lon pair </p>
          <form id="NDVI_Form" action="/timeseries" method="post" > 
          Lat/Lons: <input size="80" type="text" name='lat_lng_string' id="lat_lng_string" value="" /></form>
          <input type="submit" class="button" value="Get NDVI Time Series for Marker Locations" name="gridmetForm" form="NDVI_Form" />
        </div>
        <div id="map-canvas"></div>
        <div id="chart_div"></div>
      </div>
  </body> 
</html>
"""
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_PAGE_HTML)      
        # UserLatLongValue = self.request.get('lat_lon_string')    
        # print(UserLatLongValue)
        # pylint: disable=g-bad-name
        # """Request an image from Earth Engine and render it to a web page."""
        # ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
        # mapid = ee.Image('srtm90_v4').getMapId({'min': 0, 'max': 1000})

        # These could be put directly into template.render, but it
        # helps make the script more readable to pull them out here, especially
        # if this is expanded to include more variables.
        # template_values = {            
        #    'UserLatLongValue': UserLatLongValue
        # }
        # template = jinja_environment.get_template('index.html')
        # self.response.write(template.render(template_values))

        #### A function to compute NDVI for a Landsat image.

class Timeseries(webapp2.RequestHandler):
    def post(self):        
        """Request an image from Earth Engine and render it to a web page."""
        ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)

        #### Grabs data from "name" in the HTML form tags
        # factor = float(cgi.escape(self.request.get('factor')))
        # startdate = cgi.escape(self.request.get('startdate'))
        startdate = '2011-01-01'
        enddate = '2014-12-30'

        ##GRABS THE LAT LONG STRING FROM HTML FORM
        UserLatLong = cgi.escape(self.request.get('lat_lng_string'))
        print(UserLatLong)
        UserLatLongX = UserLatLong.split(",")
        # print(UserLatLongX)

        #TURN EACH STRING IN LIST TO A FLOAT FOR LAT,LONG
        UserLat = map(float,UserLatLongX[0::2])
        UserLong = map(float,UserLatLongX[1::2])

        # print(UserLat)
        # lat_lon_tuple = zip(UserLatLongX[0::2], UserLatLongX[1::2])
        # print(lat_lon_tuple)

        #### CLOUD MASK FUNCTION 
        def common_area_func(refl_toa):
            #### Common area
            common_area = refl_toa.mask().reduce(ee.call("Reducer.and"))
            refl_toa = refl_toa.mask(common_area)
            #### Cloud mask
            cloud_mask = ee.Algorithms.Landsat.simpleCloudScore(refl_toa) \
                .select(['cloud']).lt(ee.Image.constant(50))
            return refl_toa.mask(cloud_mask.mask(cloud_mask))

        #### Function to calc NDVI using .map method
        def ndvi_calc_L5L7(refl_toa): 
            refl_toa = common_area_func(refl_toa)
            ndvi_img = refl_toa.select("B4", "B3").normalizedDifference().select([0],['NDVI'])
            return ee.Image(ndvi_img.copyProperties(refl_toa,['system:index','system:time_start','system_time_end']))

        def ndvi_calc_L8(refl_toa): 
            refl_toa = common_area_func(refl_toa)
            ndvi_img = refl_toa.select("B5", "B4").normalizedDifference().select([0],['NDVI'])
            return ee.Image(ndvi_img.copyProperties(refl_toa,['system:index','system:time_start','system_time_end']))                

        master_dict=[]
        for i in range(len(UserLat)):          

            point = ee.Feature.Point(float(UserLong[i]),float(UserLat[i]));            

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
            t0 = time.time()
            while True:
                try:
                    extract = image_coll_ndvi_mrg_L5L7L8.getRegion(point,1).getInfo();
                    break
                except:
                    print("   Resending...")
                    time.sleep(0.5)
                    pass
            extract.pop(0) #remove first row of list ["id","longitude","latitude","time","NDVI"]

            t1 = time.time()
            print('elapsed time = {0} seconds'.format(t1-t0))
            # extract.pop(0) #remove first row of list ["id","longitude","latitude","time","NDVI"]
            # extractslice = [arr[i][0:2] for i in range(0,2)]
            # extract = list(zip(*extract)[4])
            # for sublist in extract:
                # del sublist[3]
            ##time_list = [row[3] for row in extract]
            ##ndvilist = [row[4] for row in extract]        
            # time_list = [datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y,%m,%d") for x in time_list]
            ##temp_arr = zip(time_list,ndvilist)
            ##temp_arr = [(row[3], row[4]) for row in extract]

            #### CREATE TIME SERIES ARRAY WITH DATE IN COL 1 AND VALUE IN COL 2
            TimeSeries_list = []
            for ftr in extract:
                # print ftr[3]
                # print type(ftr[3])
                # print ftr[4]
                # print type(ftr[4])
                ##if ftr[4] is not None:
                ##    TimeSeries_list.append([int(ftr[3]), float(ftr[4])])
                try:
                    TimeSeries_list.append([int(ftr[3]), float(ftr[4])])
                except (TypeError, ValueError) as e:
                    pass

            #### SORT IN CHRONOLOGICAL ORDER
            # TimeSeries_array.sort(key=lambda date: datetime.datetime.strptime(date[0], "%m/%d/%Y"))
            ##TimeSeries_list.sort(key = lambda col: col[0])
            TimeSeries_list.sort()

            #### ADD HEADER TO SORTED LIST 
            # TimeSeries_array = [['Dates','NDVI']] + TimeSeries_array
            # print(TimeSeries_array)

            #### FILTER OUT "None" VALUES (OLD METHOD)
            # ndvilist_filt = [x for x in ndvilist if x is not None] 

            #### CALCULATE NDVI STATS 
            # meanNDVI = numpy.mean(ndvilist_filt,axis=0)
            # medianNDVI = numpy.median(ndvilist_filt,axis=0)
            # maxNDVI = numpy.max(ndvilist_filt,axis=0)
            # minNDVI = numpy.min(ndvilist_filt,axis=0)
            ## These could be put directly into template.render, but it
            ## helps make the script more readable to pull them out here, especially
            ## if this is expanded to include more variables.

            #### COLOR MAP SPECTRUM
            # viz_params = {
            #     'min':0,
            #     'max':0.4, 
            #     'palette':"000000,7F0000,FF0000,FFA500,F5F5DC,D2B38C,40E0D0,7FFF00,006400,0000FF,FF00FF"
            # }

            #### GRAB MAPPING PARAMETER TO USE IN TEMPLATE VALUES
            # mapid = image_coll_ndvi_mrg_L5L7L8.median().getMapId(viz_params)
            temp_dict = {}
            temp_dict['name'] = str(float(UserLat[i])) + ',' + str(float(UserLong[i]))
            temp_dict['data'] = TimeSeries_list
            # temp_dict = sorted(temp_dict,reverse=True)
            # print(temp_dict)
            # sorted(temp_dict,reverse=True)
            # print(temp_dict)
            master_dict.append(temp_dict)
            
        
        master_dict_json = json.dumps(master_dict)
        # print(master_dict_json)
        # print master_dict_json


        template_values = {
            # 'mapid': mapid['mapid'],
            # 'token': mapid['token'],
            # 'ndvilist_filt': ndvilist_filt,
            # 'meanNDVIvalue': meanNDVI,
            # 'medianNDVIvalue': medianNDVI,
            # 'maxNDVIvalue': maxNDVI,
            # 'minNDVIvalue': minNDVI,
            # 'mapid': mapid['mapid'],
            # 'token': mapid['token'],
            'UserLatLongValue': UserLatLong,
            'TimeSeries_array': master_dict_json
        }
        template = jinja_environment.get_template('index.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/timeseries',Timeseries)], debug=True)

