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
        mp = ogr.Geometry(ogr.wkbMultiPoint)
        prev_time = self.data[0][0]
        prev_vel = self.data[0][3]

        shpDriver = ogr.GetDriverByName("ESRI Shapefile")
        fieldName = 'stop'
        fieldType = ogr.OFTString
        fieldValue = 'stop'
        if os.path.exists(filename):
            shpDriver.DeleteDataSource(filename)
        outDataSource = shpDriver.CreateDataSource(filename)
        outLayer = outDataSource.CreateLayer(filename, geom_type=ogr.wkbMultiPoint )
        # create a field
        idField = ogr.FieldDefn(fieldName, fieldType)
        outLayer.CreateField(idField)
        for row in self.data:
            if (prev_vel <= threshold and row[0] - prev_time >= duration and row[3] <= threshold):
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(row[2], row[1])
                mp.AddGeometry(point)
            prev_time = row[0]
            prev_vel = row[3]
        # Create the feature and set values
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(mp)
        outFeature.SetField(fieldName, fieldValue)
        outLayer.CreateFeature(outFeature)

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
        




