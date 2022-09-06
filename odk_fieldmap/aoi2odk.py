#!/bin/python3

import sys, os
import json

from geo_utils import get_extent_bbox
from geo_utils import make_centroids
from geo_utils import osm_json_to_geojson
from overpass import query
    
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
    return overpass_json

def aoi2project(AOIfile):
    """
    Takes a GeoJSON file with an aoi polygon, creates
    - A GeoJSON of all the OSM building polygons in it
    - A GeoJSON of the centroids thereof
    - 
    """
    (AOIpath, ext) = os.path.splitext(AOIfile)
    buildings = get_buildings(AOIfile)
    
    buildings_json = AOIpath + '_buildings.json'
    with open(buildings_json, 'w') as bj:
        json.dump(buildings, bj)

    buildings_geojson = AOIpath + '_buildings.geojson'
    geojson = osm_json_to_geojson(buildings_json)
    with open(buildings_geojson, 'w') as of:
        of.write(geojson)
    # Use the Node-based osmtogeojson module
    # Why? Horrifying details in geo_utils docstring
    make_centroids(buildings_geojson)

if __name__ == "__main__":
    """
    If run from CLI, attempts to convert a GeoJSON
    AOI into a project on an ODK Central server
    with multiple forms corresponding to sub-areas
    of the AOI.
    """
    AOIfile = sys.argv[1]
    aoi2project(AOIfile)
