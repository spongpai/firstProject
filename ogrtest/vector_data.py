__author__ = 'ing'

# script to count features
# import modules
import ogr, os, sys
import gdal

# set the working directory
os.chdir('/home/ing/PycharmProjects/firstProject/data/ospy_data1')
# get the driver
driver = ogr.GetDriverByName('ESRI Shapefile')
# open the data source
inDS = driver.Open('sites.shp', 0)
if inDS is None:
    print 'Could not open file'
    sys.exit(1)
# get the data layer
inLayer = inDS.getLayer()

'''
# loop through the features and count them
cnt = 0
feature = layer.GetNextFeature()
while feature:
    cnt = cnt + 1
    feature.Destroy()
    feature = layer.GetNextFeature()
print 'There are ' + str(cnt) + ' features'

# close the data source
datasource.Destroy()
'''

# create a new data source and layer
if os.path.exists('test.shp'):
    driver.DeleteDataSource('test.shp')
outDS = driver.CreateDataSource('test.shp')
if outDS is None:
    print 'Could not create file'
    sys.exit(1)
outLayer = outDS.CreateLayer('test', geom_type=ogr.wkbPoint)

# use the input FieldDefn to add a field to the output
fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('id')
outLayer.CreateField(fieldDefn)

# get the FeatureDefn for the output layer
featureDefn = outLayer.GetLayerDefn()

# loop through the input features
cnt = 0
inFeature = inLayer.GetNextFeature()
while inFeature:
    # create a new feature
    outFeature = ogr.Feature(featureDefn)
    outFeature.SetGeometry(inFeature.GetGeometryRef())
    outFeature.SetField('id', inFeature.GetField('id'))
    # add the feature to the output layer

    outLayer.CreateFeature(outFeature)
    # destroy the features
    inFeature.Destroy()
    outFeature.Destroy()
    # increment cnt and if we have to do more then keep looping
    cnt = cnt + 1
    if cnt < 10: inFeature = inLayer.GetNextFeature()
    else: break

#close the data sources
inDS.Destroy()
outDS.Destroy()
