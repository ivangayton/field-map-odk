#!/usr/bin/python3
"""
Various utilities for using GDAL in python
"""
import sys, os

from osgeo import ogr

def get_ogr_driver(extension):
    """Load a driver from GDAL for the input file. 
       Only GeoJSON guaranteed to work.
    """
    driver = None
    if extension.lower() == '.shp':
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif extension.lower() == '.geojson':
        driver = ogr.GetDriverByName('GeoJSON')
    elif extension.lower() == '.kml':
        driver = ogr.GetDriverByName('KML')
    elif extension.lower() == '.gpkg':
        driver = ogr.GetDriverByName('GPKG')
    else:
        print('Check input file format for {}'.format(infile))
        sys.exit()
    return driver

def get_extent(infile, extension):
    try:
        driver = get_ogr_driver(extension)
        datasource = driver.Open(infile, 0)
        layer = datasource.GetLayer()
        extent = layer.GetExtent()
        (xmin, xmax, ymin, ymax) = (extent[0], extent[1], extent[2], extent[3])
        return (xmin, xmax, ymin, ymax)
    except Exception as e:
        print('Something went wrong with the ogr driver')
        print(e)
        exit(1)

def get_extent_bbox(infile, extension):
    """
    Returns a string in the format of a bbox that
    works with an Overpass query.
    """
    try:
        driver = get_ogr_driver(extension)
        datasource = driver.Open(infile, 0)
        layer = datasource.GetLayer()
        extent = layer.GetExtent()
        (xmin, xmax, ymin, ymax) = (extent[0], extent[1], extent[2], extent[3])
        return f'{ymin},{xmin},{ymax},{xmax}'
    except Exception as e:
        print('Something went wrong with the ogr driver')
        print(e)
        exit(1)

def get_centroids(geojson):
    """
    Expects a GeoJSON string of polygons (I know, this is not
    consistent with the other functions, sue me).
    Returns a GeoJSON string of centroids.
    Retains all fields from the original polygon file.
    """

    inDriver = get_ogr_driver('geojson')
    inDatasource = inDriver.Open(geojson)
    inLayer = inDatasource.GetLayer()
    inLayerDefn = inLayer.GetLayerDefn()

    outDriver = get_ogr_driver('geojson')
    outDataSource = outDriver.CreateDataSource(outdata)
    outLayer = outDataSource.CreateLayer("centroids", geom_type=ogr.wkbPoint)
    outLayerDefn = outLayer.GetLayerDefn()

    # Get the fields (attributes)
    inFields = []
    for i in range(0, inLayerDefn.GetFieldCount()):
        inFields.append(inLayerDefn.GetFieldDefn(i))

    for i in range(0, inlayer.GetFeatureCount()):
        inFeature = inLayer.GetFeature(i)
        outFeature = ogr.Feature(outLayerDefn)
        # TODO add the fields
        geom = inFeature.GetGeometryRef()
        centroid = geom.Centroid()
        outFeature.SetGeometry(centroid)
        outLayer.CreateFeature(outFeature)
        # Save and close input and output features
        inFeature = None
        outFeature = None

    

    return
    

    
        
def get_geomcollection(infile, extension):
    try:
        driver = get_ogr_driver(extension)
        datasource = driver.Open(infile, 0)
        layer = datasource.GetLayer()
        extent = layer.GetExtent()
        (xmin, xmax, ymin, ymax) = (extent[0], extent[1], extent[2], extent[3])
        featurecount = layer.GetFeatureCount()
        geomcollection = ogr.Geometry(ogr.wkbGeometryCollection)

        # using a horrible range iterator to work around an apparent bug in OGR
        # (layer won't iterate in some versions of OGR)
        for i in range(featurecount):
            feature = layer.GetNextFeature()
            geomcollection.AddGeometry(feature.GetGeometryRef())
        return geomcollection
    except Exception as e:
        print('Something went wrong with the ogr driver')
        print(e)
        exit(1)

    
