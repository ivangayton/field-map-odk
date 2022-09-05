#!/bin/python3

import sys, os
from .geo_utils import get_extent_bbox
from .overpass import query
from osm2geojson import json2geojson
import json



def aoi2project(aoi):
    """
    Takes a GeoJSON file with an aoi polygon, creates
    - A GeoJSON of all the OSM building polygons in it
    - A GeoJSON of the centroids thereof
    - 
    """
    pass

def building_centroids(aoi_file):
    """
    Given a GeoJSON AOI polygon, returns a centroid for every
    OSM building polygon within it.
    """
    (infilepath, extension) = os.path.splitext(aoi_file)
    extent = get_extent_bbox(aoi_file, extension)
    querystring = (
        f'[out:json][timeout:200];'
        f'(wr["building"]({extent}););'
        f'out body;>;out body;'
    )
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    overpass_json = query(querystring, overpass_url)
    gj = json2geojson(overpass_json)
    
    return gj

if __name__ == "__main__":
    """
    If run from CLI, attempts to convert a GeoJSON
    AOI into a project on an ODK Central server
    with multiple forms corresponding to sub-areas
    of the AOI.
    """
    buildings = building_centroids(sys.argv[1])
    print(type(buildings))
    with open('test/test.geojson','w') as outfile:
        json.dump(buildings, outfile)
        
    
