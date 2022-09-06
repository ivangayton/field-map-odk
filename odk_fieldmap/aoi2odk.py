#!/bin/python3

import sys, os
import json

from geo_utils import get_extent_bbox
from geo_utils import make_centroids
from overpass import query

from osm2geojson import json2geojson
    
def get_buildings(aoi_file):
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
    overpass_url = ('https://overpass.kumi.systems'
                    '/api/interpreter')
    overpass_json = query(querystring, overpass_url)
    return json2geojson(overpass_json)

def aoi2project(AOIfile, formfile):
    """
    Takes a GeoJSON file with an aoi polygon, creates
    - A GeoJSON of all the OSM building polygons in it
    - A GeoJSON of the centroids thereof
    - 
    """
    (AOIpath, ext) = os.path.splitext(AOIfile)
    buildings = get_buildings(AOIfile)
    buildings_file = AOIpath + '_buildings' + ext
    with open(buildings_file, 'w') as bf:
        json.dump(buildings, bf)
    make_centroids(buildings_file)

if __name__ == "__main__":
    """
    If run from CLI, attempts to convert a GeoJSON
    AOI into a project on an ODK Central server
    with multiple forms corresponding to sub-areas
    of the AOI.
    """
    AOIfile = sys.argv[1]
    formfile = sys.argv[2]
    aoi2project(AOIfile, formfile)
