# field-map-odk
Utilities to create ODK assets for field mapping

ODK now has a Select From File (Map) function.

This is great, but it requires the person creating the ODK project to specify the map file the person will be selecting from (OMK didn't require this---the mapper could just grab OSM data from their phone---but that came with a tradeoff: it inherently limited OMK to using OSM data; no other kind of map data could be used).

This is a set of utility scripts to automate the process of

- Taking a particular mapper's ID (probably OSM ID)
- Taking the Area of Interest that they will be mapping
- Downloading the relevant features from OSM and creating a point GeoJSON file for them
- Creating a form from a template for that mapper, refering to the relevant GeoJSON file
- Pushing the form and GeoJSON file to a specified ODK project
- Creating an app user for the mapper with view permission for the relvant form
- Returning a QR code for that app user

## Users
## Campaign managers
Campaign managers select an Area of Interest (AOI) and organize field mappers to go out and collect data. They need to:
- Select an AOI polygon by creating a GeoJSON or by tracing a polygon in a Web map
- Choose a task division scheme (number of features or area per task, and possibly variations on what features to use as the preffered splitting lines)
- Provide specific instructions and guidance for field mappers on the project.
- Provide a URL to a mobile-friendly Web page where field mappers can, from their mobile phone, select an task that is not already "checked out" (or possibly simply allocate areas to the field mappers).
- See the status of tasks (open, "checked out", completed but not validated, requires rework, validated, etc) in the Web browser on their computer

## Field mappers
Field mappers select (or are allocated) individual tasks within a project AOI and use ODK Collect to gather data in those areas. They need to:
- Visit a mobile-friendly Web page where they can see available tasks on a map
- Choose an area and launch ODK Collect with the form corresponding to their allocated area pre-loaded

## Validators
Validators review the data collected by field mappers and assess its quality. If the data is good, the validators merge the portion of the data that belongs in OpenStreetMap to OSM. If it requires more work, the validators either fix it themselves (for minor stuff like spelling or capitalization mistakes that don't seem to be systematic) or inform the field mappers that they need to fix it. They need to:
- Access completed data sets of "submissions" as Comma Separated Values and/or OSM XML so that they can review it.
- Mark areas as validated or requiring rework
- Communicate with field mappers if rework is necessary
- Merge good-quality data into OSM (probably from JOSM).
- Mark areas as completed and merged.


# Info for developers

The basic setup here is:

- An ODK Central server which functions as the back end for the field data collectors' ODK Collect apps on their Android phones. Devs must have access to an ODK Central server with a username and password granting admin credentials.
  - [Here are the instructions for setting up an ODK Central server on Digital Ocean](https://docs.getodk.org/central-install-digital-ocean/) (it's very similar on AWS or whatever)
- A computer-screen-optimized web app that allows campaign managers to:
  - Select AOIs
  - Choose task-splitting schemes
  - Provide instructions and guidance specific to the project
  - View areas that are at various stages of completion
  - Provide a project-specific URL that field mappers can access from their mobile phones to select and map tasks.
- A back end that converts the project parameters into a corresponding ODK Central project. This must:
  - Convert the AOI into a bounding box
  - Download the OSM features that will be mapped in that bounding box (buildings and/or amenities) as well as the OSM features 
  - Trim the features within the bounding box but outside the AOI polygon
  - Convert the polygon features into centroid points (needed because ODK select from map doesn't yet deal with polygons; it will in future)
  - Use line features as cutlines to create individual tasks (squares don't make sense for field mapping, neighborhoods delineated by large roads, watercourses, and railways do)
  - Split the AOI into those tasks
  - Use the ODK Central API to create:
    - A project for the whole AOI
    - Forms for each split task
    - GeoJSON feature collections for each form
    - An App User for each form
  - Grab the settings (and QR codes) for each app user and forward them to the task selection Web app.
  


  - Ideally with a link that opens ODK Collect directly from the browser, but if that's hard, the fallback is downloading a QR code and importing it into ODK Collect.

