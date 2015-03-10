__author__ = 'siripening'

import MySQLdb as mysqldb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import csv
import random
from scipy.interpolate import griddata
from math import sqrt
from dateutil import rrule
from datetime import datetime, timedelta
from functools import wraps
from time import time
from maptile.tilename import latlon_unit, tileXY
from maptile.closet_pair import closestPair
from plotmap import plot
import sklearn.metrics.pairwise
import scipy.spatial.distance

def open_mysql_connection(database):
    try:
        cnx = mysqldb.connect(user='event', passwd='eventshop', host='eventshop.ics.uci.edu', port=3306, db=database)
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
    return cnx


def close_mysql_connection(cnx):
     if cnx is not None:
        cnx.close()

# get hourly data from the table 'hourly_sample'
# return three arrays: points[latitude, longitude], and measurement
def get_hourly_data(i_date, i_time):

    lat = []; lon = []; val = []

    # Try to connect
    cnx = open_mysql_connection('test')
    if cnx is None:
        print('The database could not connect')
    else:
        print('The database could connect')
        query = ("SELECT site_num, latitude, longitude, date_local, time_local, sample_measurement"
                 " FROM hourly_sample "
                 " WHERE  (date_local = %s) AND (time_local =%s) AND POC!='4' "
                 " AND (latitude < 45.60 AND latitude > 25.69) "
                 " AND (longitude < -67.73 AND longitude > -84.59 ) ")
                 #" AND (latitude < 42.0095 AND latitude > 32.5343) "
                 #" AND (longitude > -124.4096 AND longitude < -114.1308) ")
        #i_date = datetime.date(2014,1,1)
        #i_time = datetime.time(0,0,0)
        try:
            #print query
            cursor = cnx.cursor()
            cursor.execute(query, (i_date, i_time))

            for (site_num, latitude, longitude, date_local, time_local, sample_measurement) in cursor:
                #print("{}, [{},{}] measure on {:%d %b %Y}:{} value is {}".
                #      format(site_num, latitude, longitude, date_local, time_local, sample_measurement))
                lat.append(latitude)
                lon.append(longitude)
                val.append(sample_measurement)
            #points = [[x, y] for x in lat for y in lon]
        except mysqldb.Error, e:
             print "Error %d: %s" % (e.args[0], e.args[1])

        finally:
            if cnx is not None:
                cnx.close()
    return (np.asarray(lat), np.asarray(lon), np.asarray(val))

def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    print "%s (%s) took %f time to finish" % (f.__name__,args[3], elapsed)
    write_csv('runtime.csv', "%s zoom_level:%s grid_size:%s #point:%s run_time: %f" % (f.__name__, args[5], args[3],
                                                                                       len(lat), elapsed))
    return result
  return wrapper

@timed
def nearest_interpolation(lat, lon, values, grid_size, test_index, zoom_level, date, time):
    min_lat = lat.min()
    max_lat = lat.max()
    min_lon = lon.min()
    max_lon = lon.max()
    lat_len = max_lat - min_lat
    lon_len = max_lon - min_lon
    if(lat_len>lon_len):
        max_len = lat_len
    else:
        max_len = lon_len

    test_lat = []; test_lon = []; test_val = []
    grid_x, grid_y = np.mgrid[min_lat:max_lat:grid_size[0], min_lon:max_lon:grid_size[1]]
    print min_lat, max_lat, min_lon, max_lon, grid_size
    train_lat = np.delete(lat, test_index)
    train_lon = np.delete(lon, test_index)
    train_val = np.delete(values, test_index)

    grid_z = griddata((train_lat,train_lon), train_val, (grid_x, grid_y), method='linear')

    se = []; se2 = []
    for item in test_index:
        x,y = tileXY(lat[item]-min_lat, lon[item]-min_lon, zoom_level)
        xi = int((lat[item] - min_lat)//grid_size[0])
        yi = int((lon[item] - min_lon)//grid_size[1])
        print x, y, xi, yi
        z_value = grid_z[xi,yi]
        #z_value2 = grid_z[x,y]
        see = ((values[item] - z_value) ** 2)
        #see2 = ((values[item] - z_value2) ** 2)
        se.append(see)
        #se2.append(see2)
        print item, lat[item], lon[item], xi, yi, values[item], z_value, see, x, y#, z_value2, see2, zoom_level
        write_csv('error_testing_point_0308.csv', result=(date, time, item, lat[item], lon[item], zoom_level, xi, yi,
                                                          values[item],
                                                          z_value, see#, x,y,
        # z_value2,see2
                                               ))
    rmse = np.asarray(se).mean()
    #rmse2=np.asarray(se2).mean()
    print "rootmeansquare: ", sqrt(rmse)
    return grid_x, grid_y, grid_z, min_lat, min_lon, rmse#, rmse2

def write_csv(file, result):
    with open(file, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(result)

def random_subset(iterator, N):
    result = []
    i = 0

    for item in iterator:
        i += 1
        if len(result) < N:
            result.append(item)
        else:
            s = int(random.random() * i)
            if s < N:
                result[s] = item

    return result

def show_original():
    lat, lon, values = get_hourly_data('2014-01-01', '00:00:00')
    plt.figure(1)
    gs = gridspec.GridSpec(1, 2)
    plt.subplot(gs[0,0])
    plt.scatter(lat, lon, c=values, s=20)
    plt.colorbar()
    plt.title('Original')

    plt.subplot()
    plt.show()

def test():
    #time = datetime.time(0,0,0)
    #day = datetime.date(2014,1,1)
    start = datetime(2014, 1, 1, 0, 0 ,0)
    hundredDaysLater = start + timedelta(days=1)
    i = 0
    for dt in rrule.rrule(rrule.HOURLY, dtstart=start, until=hundredDaysLater):
        i = i + 1
        print '-------\n', dt.date(), dt.time()
        lat, lon, values = get_hourly_data(dt.date(), dt.time())
        #print points
        #print values
        grid_level = range(6, 19) #0.001 unit is too small
        error = np.zeros((len(grid_level), 5))

        for j in range(0, 5):
            #test_index = random.randint(0, lat.size)
            test_index = random_subset(range(0,lat.size), 5)    # remove ten points as a test data set
            gs = gridspec.GridSpec(3, 5)
            plt.figure(i)
            plt.subplot(gs[0,0])
            # show result
            #plt.scatter(lat, lon, c=values, s=20)
            plot(lat, lon, values)
            #plt.colorbar()
            plt.title('Original')
            print("origin std: ", values.std())
            for level in grid_level:
                #print len(lat), len(lon), len(values)
                #plt.figure(1)
                grid_unit = latlon_unit(level)
                grid_x, grid_y, grid_z, min_lat, min_lon, se = nearest_interpolation(lat, lon, values, grid_unit,
                                                                                     test_index, level, dt.date(), dt.time())
                print("datetime:", dt.date(), dt.time(), "nearest:", grid_unit, "std:", np.nanstd(grid_z),"level:", level, "rms:", se)
                write_csv('error_level_0308.csv', result=("datetime:", dt.date(), dt.time(), ",level:",  level, ","
                                                                                                                "nearest:", grid_unit, ",std:", np.nanstd(grid_z), ",rms:", se))
                error[level-6,j] = se
                plt.subplot(gs[(level-5)/5,(level-5)%5])
                plt.contourf(grid_x,grid_y,grid_z)
                plt.colorbar()
                plt.title("%d[%1.3f,%1.3f]%1.5f" % (level, grid_unit[0], grid_unit[1], sqrt(se)))
            #plt.show()
        print error
        #rmse =  np.sqrt(error.mean(axis=1))
        rmse = error.mean(axis=1)
        write_csv("error_rmse_0308.csv", result=(i,rmse[0],rmse[1],rmse[2],rmse[3],rmse[4],rmse[5],rmse[6],rmse[7],
                                                 rmse[8],rmse[9],rmse[10]))

if __name__ == "__main__":
    lat, lon, values = get_hourly_data('2014-01-01', '00:00:00')
    lat=np.array(lat)
    lon=np.array(lon)
    latlon = np.vstack((lat,lon)).T
    #plot(lat, lon, values)
    #plt.show()
    dists = scipy.spatial.distance.pdist(latlon, 'cityblock')

    print np.sort(dists)
    #d = filter(lambda a: a != 0., dists)
    print "min %1.5f, max %1.5f" % (np.min(dists), np.max(dists))

    print closestPair(lat)
    print closestPair(lon)
    #show_original()
    test()
    #a = [1,2,3,5,81,87,42,6]
    #print random_subset(a, 5)