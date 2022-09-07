#!/bin/python3

import sys, os

from odk_requests import create_project
from odk_requests import project_id
from odk_requests import create_form

def formdir2project(url, aut, indir):
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
    print(f'Creating a project called {name}.\n')
    # TODO: first check that project does not exist
    # Create it

    from time import sleep
    sleep(2)
    
    create_project(url, aut, name)
    # Need its numerical id for future operations
    pid = project_id(url, aut, name)
    print(f'The new project ID is {pid}./n')
    return pid

def push_forms(url, aut, pid, indir):
    """
    """
    formdir = os.path.join(indir, 'forms')
    geojsondir = os.path.join(indir, 'geojson')
    
    # Traverse the directory of xlsforms
    filelist = os.listdir(formdir)
    # keep only the files that are xlsx
    # TODO: Maybe reject all non-point input files
    forms = [x for x in filelist if
             os.path.splitext(x)[1].lower()
             == '.xlsx']
    print(f'I found {len(forms)} forms to upload')
    for form in forms:
        formname = (os.path.splitext
                    (os.path.basename(form))[0])
        print(f'Uploading form {form}.')
        formpath = os.path.join(formdir, form)
        formfile = open(formpath, 'rb')
        formdata = formfile.read()
        r = create_form(url, aut, pid,
                        formname, formdata)
        print(r)
    return 'yo'

if __name__ == '__main__':
    indir = sys.argv[1]
    url = sys.argv[2]
    aut = (sys.argv[3], sys.argv[4])
    print('\nHere goes nothing.\n')
    pid = formdir2project(url, aut, indir)
    print(f'We have a project with id {pid}.') 
    whatever = push_forms(url, aut, pid, indir)
    
    
