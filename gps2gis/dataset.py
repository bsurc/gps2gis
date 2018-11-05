import csv
import datetime
import numpy as np
import os
from osgeo import ogr
from scipy.spatial import ConvexHull
import time

class Dataset:
    def __init__(self, filename):
        self.filename = filename
        self._read_file()




    def _read_file(self):
        temp_array = []
        with open(self.filename, 'r', newline='') as in_file:
            reader = csv.reader(in_file, delimiter='\t')
            next(reader, None) # Skip header
            for row in reader:
                tsp = int(time.mktime(datetime.datetime.strptime("{} {}".format(row[0], row[1]), "%Y/%m/%d %H:%M:%S").timetuple()))
                lat = float(row[2])
                lon = float(row[3])
                vel = float(row[4])
                alt = float(row[5])
                temp_array.append([tsp, lat, lon, vel, alt])
        self.data = temp_array


    def write_multipoint(self, filename, threshold, duration):
        ## Inititalize Driver and output file
        mp = ogr.Geometry(ogr.wkbMultiPoint)
        shpDriver = ogr.GetDriverByName("ESRI Shapefile")
        fieldName = 'Stop_Time'
        fieldType = ogr.OFTInteger
        if os.path.exists(filename):
            shpDriver.DeleteDataSource(filename)
        outDataSource = shpDriver.CreateDataSource(filename)
        outLayer = outDataSource.CreateLayer(filename, geom_type=ogr.wkbMultiPoint )
        idField = ogr.FieldDefn(fieldName, fieldType)
        outLayer.CreateField(idField)

        ## Some variables to track stops
        stopped = False
        stop_time = None
        prev_time = self.data[0][0]
        prev_vel = self.data[0][3]

        ## Loop over rows
        for row in self.data:
            if (prev_vel <= threshold and row[0] - prev_time >= duration and row[3] <= threshold):
                if not stopped:
                    stopped = True
                    stop_time = prev_time
            else:
                if stopped:
                    stopped = False                    
                    ## Create point and add as feature
                    point = ogr.Geometry(ogr.wkbPoint)
                    point.AddPoint(row[2], row[1])
                    mp.AddGeometry(point)
                    featureDefn = outLayer.GetLayerDefn()
                    outFeature = ogr.Feature(featureDefn)
                    outFeature.SetGeometry(mp)
                    outFeature.SetField(fieldName, row[0] - stop_time)
                    outLayer.CreateFeature(outFeature)
                    ## Reset time
                    stop_time = None
            ## Set previous values to watch
            prev_time = row[0]
            prev_vel = row[3]

    def write_polygon(self, filename, threshold, duration, merge=False):
        stop_events = []
        current_stop = None
        prev_time = self.data[0][0]
        prev_vel = self.data[0][3]
        
        for row in self.data:
            if (prev_vel <= threshold and row[0] - prev_time >= duration and row[3] <= threshold):
                if current_stop is None:
                    current_stop = [[row[2], row[1]]]
                else:
                    current_stop.append([row[2], row[1]])
            else:
                if current_stop is not None:
                    if len(current_stop) > 2:
                        stop_events.append(current_stop)
                    current_stop = None
            prev_time = row[0]
            prev_vel = row[3]
        
        to_union = ogr.Geometry(ogr.wkbMultiPolygon)
        for event in stop_events:
            try:
                hull = ConvexHull(np.array(event))
                ring = ogr.Geometry(ogr.wkbLinearRing)
                for index in hull.vertices:
                    ring.AddPoint(event[index][0], event[index][1])
                ring.AddPoint(event[hull.vertices[0]][0], event[hull.vertices[0]][1])
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
                to_union.AddGeometry(poly)
            except:
                pass

        union = to_union.UnionCascaded()

        shpDriver = ogr.GetDriverByName("ESRI Shapefile")
        fieldName = 'stop'
        fieldType = ogr.OFTString
        fieldValue = 'stop'
        if os.path.exists(filename):
            shpDriver.DeleteDataSource(filename)
        outDataSource = shpDriver.CreateDataSource(filename)
        outLayer = outDataSource.CreateLayer(filename, geom_type=ogr.wkbPolygon )
        idField = ogr.FieldDefn(fieldName, fieldType)
        outLayer.CreateField(idField)
        featureDefn = outLayer.GetLayerDefn()
        for i in range(0, union.GetGeometryCount()):
            g = union.GetGeometryRef(i)
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(g)
            outFeature.SetField(fieldName, fieldValue)
            outLayer.CreateFeature(outFeature)
        outDataSource = None
        




