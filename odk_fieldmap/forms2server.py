#!/bin/python3

import sys, os

from odk_requests import create_project
from odk_requests import project_id
from odk_requests import create_form
from odk_requests import forms
from odk_requests import attach_to_form
from odk_requests import publish_form

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

    name = (os.path.basename(
        indir.rstrip(os.path.sep)))
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
    Push all of the forms in the subdirectory forms
    of the input directory up to the ODK Central server.
    """
    formdir = os.path.join(indir, 'forms')
    
    
    # Traverse the directory of xlsforms
    filelist = os.listdir(formdir)
    # keep only the files that are xlsx
    # TODO: Maybe reject all non-point input files
    forms = [os.path.splitext(x)[0]
             for x in filelist if
             os.path.splitext(x)[1].lower()
             == '.xlsx']
    print(f'I found {len(forms)} forms to upload')
    for form in forms:
        print(f'Uploading form {form}.')
        formpath = os.path.join(formdir,
                                f'{form}.xlsx')
        formfile = open(formpath, 'rb')
        formdata = formfile.read()
        rf = create_form(url, aut, pid,
                        form, formdata)
        print(rf)
    return forms
    
def push_geojson(url, aut, pid, indir):
    """
    Push all of the geojson attachments to their
    corresponsing forms on the ODK Central server.
    The geojson files are expected to be in the 
    geojson subdirectory of the input directory.
    """
    # TODO loop over the forms instead of the
    # files in the geojson directory.
    # Not hugely important but more consistent.
    gjdir = os.path.join(indir, 'geojson')
    filelist = os.listdir(gjdir)
    attments = [x for x in filelist if
                os.path.splitext(x)[1].lower()
                == '.geojson']
    for attment in attments:
        attname = (os.path.splitext
                    (os.path.basename(attment))[0])
        print(f'Attaching {attment}.')
        attpath = (os.path.join(gjdir, attment))
        attfile = open(attpath, 'rb')
        attdata = attfile.read()
        
        rg = attach_to_form(url, aut, pid,
                            attname, attment, attdata)
        print(rg)      
    return 'yo'

def publish_forms(url, aut, pid, forms):
    """
    """
    for form in forms:
        r = publish_form(url, aut, pid, form)
        print(r)

    
    return 'yo'

if __name__ == '__main__':
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
    indir = sys.argv[1]
    url = sys.argv[2]
    aut = (sys.argv[3], sys.argv[4])
    print('\nHere goes nothing.\n')
    pid = formdir2project(url, aut, indir)
    print(f'We have a project with id {pid}.') 
    formlist = push_forms(url, aut, pid, indir)
    print(formlist)
    whatever = push_geojson(url, aut, pid, indir)
    print(whatever)
    publish = publish_forms(url, aut, pid, formlist)
    print(publish)
    
    
