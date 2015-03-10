__author__ = 'siripening'

import MySQLdb as mysqldb
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

def open_mysql_connection(database):
    try:
        cnx = mysqldb.connect(user='event', passwd='eventshop', host='eventshop.ics.uci.edu', port=3306, db=database)
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
    return cnx


def close_mysql_connection(cnx):
     if cnx is not None:
        cnx.close()

def pm25_manual():
    #open the pm2.5 hourly data file
    data_file = open('data/pm25_station.csv')

    # create empty lists for the latitudes and longitudes
    lats, lons, site_num, value = [],[],[],[]

    # read each line in the file, and keep track of what line we are on.
    for (index, line) in enumerate(data_file.readlines()):
        # split the data into items in a list
        split_line = line.split(',')
        if(index > 0):
            lats.append(float(split_line[3]))
            lons.append(float(split_line[4]))
            site_num.append(float(split_line[2]))

    # display the first 5 lats and lons
    print('lats', lats[0:5])
    print('lons', lons[0:5])
    print('site_num', site_num[0:5])

    plot(lats, lons, site_num)


def plot(lats, lons, labels):
    max_lat = max(lats)
    min_lat = min(lats)
    max_lon = max(lons)
    min_lon = min(lons)
    span = 2
    map = Basemap(projection='merc', lat_0=(max_lat-min_lat)/2, lon_0=(max_lon-min_lon)/2,
                  resolution='h', area_thresh=0.1,
                  llcrnrlon=min_lon-span , llcrnrlat=min_lat-span,
                  urcrnrlon=max_lon+span, urcrnrlat=max_lat+span)

    map.drawcoastlines()
    map.drawcountries()
    map.fillcontinents(color='coral')
    map.drawmapboundary()

    #lons = [-135.3318, -134.8331, -134.6572]
    #lats = [57.0799, 57.0894, 56.2399]
    x,y = map(lons, lats)
    map.plot(x, y, 'bo', markersize=5)

    #for label, xpt, ypt in zip(labels, x, y):
    #    plt.text(xpt+10000, ypt+5000, label)

    #plt.show()

if __name__ == "__main__":
    pm25_manual()
    plt.show()