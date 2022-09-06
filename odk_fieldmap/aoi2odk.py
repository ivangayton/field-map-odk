#!/bin/python3

import sys, os
import json

from geo_utils import get_extent_bbox
from geo_utils import make_centroids
from overpass import query

from osm2geojson import json2geojson
from openpyxl import load_workbook


def prep_form(workbookfile, AOIfile, task_id):
    """
    Modifies the base instance of an ODK xlsform to refer
    to a specific area and GeoJSON file of features.
    N.B. Only works with OSM_Buildings_ODK_v_0-0-6.xlsx
    """
    (path, ext) = os.path.splitext(workbookfile)
    (AOIpath, AOIext) = os.path.splitext(AOIfile)
    AOIbasename = os.path.splitext(os.path.basename(AOIfile))[0]
    wb = load_workbook(filename = workbookfile)
    surveyws = wb['survey']
    settingws = wb['settings']
    
    settingws['A2'] = f'FMTM_{AOIbasename}_{task_id}'
    settingws['B2'] = f'FMTM_{AOIbasename}_{task_id}'
    surveyws['A9'] = (f'select_one_from_file '
                      f'{AOIbasename}_{task_id}{ext}')
    wb.save(f'{path}_{AOIbasename}_{task_id}{ext}')
    
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

    for i in range(0, 5):
        prep_form(formfile, AOIfile, i)
    
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
