__author__ = 'siripening'

__author__ = 'ing'
#!/usr/bin/env python
#-------------------------------------------------------
# Translates between lat/long and the slippy-map tile
# numbering scheme
#
# http://wiki.openstreetmap.org/index.php/Slippy_map_tilenames
#
# Written by Oliver White, 2007
# This file is public-domain
#
# Added more method by Siripen, 2015
#-------------------------------------------------------
from math import *

def numTiles(z):
  return(pow(2,z))

def sec(x):
  return(1/cos(x))

def latlon2relativeXY(lat,lon):
  x = (lon + 180) / 360
  y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
  return(x,y)

def latlon2xy(lat,lon,z):
  n = numTiles(z)
  x,y = latlon2relativeXY(lat,lon)
  return(n*x, n*y)

def tileXY(lat, lon, z):
  x,y = latlon2xy(lat,lon,z)
  return(int(x),int(y))

def xy2latlon(x,y,z):
  n = numTiles(z)
  relY = y / n
  lat = mercatorToLat(pi * (1 - 2 * relY))
  lon = -180.0 + 360.0 * x / n
  return(lat,lon)

def latEdges(y,z):
  n = numTiles(z)
  unit = 1 / n
  relY1 = y * unit
  relY2 = relY1 + unit
  lat1 = mercatorToLat(pi * (1 - 2 * relY1))
  lat2 = mercatorToLat(pi * (1 - 2 * relY2))
  return(lat1,lat2)

def lonEdges(x,z):
  n = numTiles(z)
  unit = 360 / n
  lon1 = -180 + x * unit
  lon2 = lon1 + unit
  return(lon1,lon2)

def tileEdges(x,y,z):
  lat1,lat2 = latEdges(y,z)
  lon1,lon2 = lonEdges(x,z)
  return((lat2, lon1, lat1, lon2)) # S,W,N,E

def mercatorToLat(mercatorY):
  return(degrees(atan(sinh(mercatorY))))

def tileSizePixels():
  return(256)

def tileLayerExt(layer):
  if(layer in ('oam')):
    return('jpg')
  return('png')

def tileLayerBase(layer):
  layers = {
    "tah": "http://cassini.toolserver.org:8080/http://a.tile.openstreetmap.org/+http://toolserver.org/~cmarqu/hill/",
	#"tah": "http://tah.openstreetmap.org/Tiles/tile/",
    "oam": "http://oam1.hypercube.telascience.org/tiles/1.0.0/openaerialmap-900913/",
    "mapnik": "http://tile.openstreetmap.org/mapnik/"
    }
  return(layers[layer])

def tileURL(x,y,z,layer):
  return "%s%d/%d/%d.%s" % (tileLayerBase(layer),z,x,y,tileLayerExt(layer))

def min_bbox(min_lat, min_lon, max_lat, max_lon, z):
    x_min_pnt, y_min_pnt = tileXY(min_lat, min_lon, z) # y_min_pnt has higher value than max_y
    x_max_pnt, y_max_pnt = tileXY(max_lat, max_lon, z)
    num_row = (1 + y_min_pnt - y_max_pnt)
    num_col = (1 + x_max_pnt - x_min_pnt)
    s_min_pnt,w_min_pnt,n_min_pnt,e_min_pnt = tileEdges(min_x,min_y,z)
    s_max_pnt,w_max_pnt,n_max_pnt,e_max_pnt = tileEdges(max_x,max_y,z)
    # return minimum bounding box (based on tile system coordinate)
    # south and west of min_pnt, north and east of max_pnt
    return s_min_pnt, w_min_pnt, n_max_pnt, e_max_pnt, num_row, num_col, num_row*num_col

def latlon_unit(z):
    latlon = []
    latlon.append([170.10226, 360.00000])
    latlon.append([85.05113, 180.00000])
    latlon.append([66.51326, 90.00000])
    latlon.append([33.25663, 45.00000])
    latlon.append([16.62832, 22.50000])
    latlon.append([8.40467, 11.25000])
    latlon.append([4.08820, 5.62500])
    latlon.append([2.04410, 2.81250])
    latlon.append([1.01460, 1.40625])
    latlon.append([0.50541, 0.70312])
    latlon.append([0.25223, 0.35156])
    latlon.append([0.12612, 0.17578])
    latlon.append([0.06303, 0.08789])
    latlon.append([0.03151, 0.04395])
    latlon.append([0.01575, 0.02197])
    latlon.append([0.00788, 0.01099])
    latlon.append([0.00394, 0.00549])
    latlon.append([0.00197, 0.00275])
    latlon.append([0.00098, 0.00137])

    return latlon[z]

if __name__ == "__main__":
  for z in range(0,19):
    #x,y = tileXY(-81.50610, -2.119888, z)
    min_lat = 25.708#32.5343# 19.117561
    max_lat = 45.60#42.0095#61.598898
    min_lon = -84.49#-124.4096#-159.36624
    max_lon = -67.73#-114.1308#-68.26090
    min_x, min_y = tileXY(min_lat, min_lon, z)
    max_x, max_y = tileXY(max_lat, max_lon, z)

    s,w,n,e = tileEdges(min_x,min_y,z)
    s2,w2,n2,e2 = tileEdges(max_x,max_y,z)
    s_box, w_box, n_box, e_box, num_row, num_col, num_tiles = min_bbox(min_lat, min_lon, max_lat, max_lon, z)

    print "%d: [%d*%d=%d] %1.5f, %1.5f, %1.5f, %1.5f, [%1.5f, %1.5f]" \
          % (z, num_row, num_col, num_tiles, s_box, w_box, n_box, e_box, (n_box-s_box)/num_row, (e_box-w_box)/num_col)
    '''
    0: [1*1=1] -85.05113, -180.00000, 85.05113, 180.00000, [170.10226, 360.00000]
    1: [1*1=1] 0.00000, -180.00000, 85.05113, 0.00000, [85.05113, 180.00000]
    2: [1*2=2] 0.00000, -180.00000, 66.51326, 0.00000, [66.51326, 90.00000]
    3: [2*3=6] 0.00000, -180.00000, 66.51326, -45.00000, [33.25663, 45.00000]
    4: [4*5=20] 0.00000, -180.00000, 66.51326, -67.50000, [16.62832, 22.50000]
    5: [6*9=54] 11.17840, -168.75000, 61.60640, -67.50000, [8.40467, 11.25000]
    6: [11*17=187] 16.63619, -163.12500, 61.60640, -67.50000, [4.08820, 5.62500]
    7: [22*33=726] 16.63619, -160.31250, 61.60640, -67.50000, [2.04410, 2.81250]
    8: [43*66=2838] 17.97873, -160.31250, 61.60640, -67.50000, [1.01460, 1.40625]
    9: [85*130=11050] 18.64625, -159.60938, 61.60640, -68.20312, [0.50541, 0.70312]
    10: [169*260=43940] 18.97903, -159.60938, 61.60640, -68.20312, [0.25223, 0.35156]
    11: [338*519=175422] 18.97903, -159.43359, 61.60640, -68.20312, [0.12612, 0.17578]
    12: [675*1038=700650] 19.06212, -159.43359, 61.60640, -68.20312, [0.06303, 0.08789]
    13: [1349*2074=2797826] 19.10365, -159.38965, 61.60640, -68.24707, [0.03151, 0.04395]
    14: [2698*4147=11188606] 19.10365, -159.36768, 61.60640, -68.24707, [0.01575, 0.02197]
    15: [5394*8293=44732442] 19.11403, -159.36768, 61.60117, -68.25806, [0.00788, 0.01099]
    16: [10788*16586=178929768] 19.11403, -159.36768, 61.60117, -68.25806, [0.00394, 0.00549]
    17: [21574*33171=715631154] 19.11662, -159.36768, 61.59987, -68.26080, [0.00197, 0.00275]
    18: [43147*66341=2862415127] 19.11662, -159.36630, 61.59921, -68.26080, [0.00098, 0.00137]
    '''

    #print "%d: [%d] %d,%d (%1.5f :: %1.5f, %1.5f :: %1.5f) " \
    #      "|| %d,%d (%1.5f :: %1.5f, %1.5f :: %1.5f)" % (z, num, min_x, min_y, s,n,w,e, max_x, max_y,s2,n2,w2,e2)

    #lon_unit = e-w
    #lat_unit = n-s
    #print "%d: %d,%d --> %1.3f :: %1.3f, %1.3f :: %1.3f :: %1.4f :: %1.4f" % (z,x,y,s,n,w,e, lon_unit, lat_unit)
    #print "<img src='%s'><br>" % tileURL(x,y,z)
