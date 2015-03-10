__author__ = 'siripening'

import os
import grass.script as grass
import grass.script.setup as gsetup
gisbase = os.environ['GISBASE']
gisdb="/your/grassdata"
location="a location"
mapset=" a mapset"
gsetup.init(gisbase, gisdb, location, mapset)
# table
desc = grass.parse_command('db.describe', flags='c', table="a_table")