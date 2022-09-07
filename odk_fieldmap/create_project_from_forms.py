#!/bin/python3

import sys, os

from odk_requests import create_project
from odk_reqeusts import project_id
from odk_requests import create_form

def forms2project(indir, url, aut):
    """
    Accepts
    - A directory full of:
      - GeoJSON files representing tasks
      - XLSForms corresponding to them
    - A base URL for an ODK Central server
    - A tuple of username and password to said server
    And creates an ODK Central project.
    Project name will be the directory name.
    """

    name = os.path.basename(indir)
    # TODO: first check that project does not exist
    # Create it
    create_project(url, aut, name)
    # Need its numerical id for future operations
    id = project_id(url, aut, name)

    formdir = os.path.join(indir, 'forms')
    geojsondir = os.path.join(indir, 'geojson')
    
    # Traverse the directory of xlsforms
    filelist = os.listdir(formdir)
    # keep only the files that are xlsx
    # TODO: Maybe reject all non-point input files
    forms = [x for x in filelist if
             os.path.splitext(x)[1].lower()
             == '.xlsx']
    for form in forms:
        create_form

    
    
    
