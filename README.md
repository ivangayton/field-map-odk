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


