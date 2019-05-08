#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 10:48:36 2019
@author: Sean

Convert digital elevation model to STL file format.

file format specifications:
input: asc (USGS DEM https://en.wikipedia.org/wiki/USGS_DEM)
output: stl (ASCII STL https://en.wikipedia.org/wiki/STL_(file_format))

notes:
    - output file x,y coordinates are in eastings/northings.
    - absent values set to 0m elevation

test data:
    - conversion has been tested with LINZ 'Wellington 1m LIDAR' dataset 
    (https://data.linz.govt.nz/layer/53621-wellington-lidar-1m-dem-2013/data/)
    e.g. file DEM_BQ31_2013_1000_1935.asc (included in repo)
    should work generally by untested.

"""
import numpy as np

#mapName='DEM_BQ31_2013_1000_1935'


mapName = raw_input("\nEnter dem file name (excl extension): ")

try:
    f=open(mapName+'.asc', 'r')
except:
    print ('\nfile %s.asc not found' % (mapName))
    exit()
    
print('\nconverting dem file %s.asc to %s.stl\n' % (mapName,mapName))

## Read dem file header lines 
header1 = f.readline()
header2 = f.readline()
xllcorner = float((f.readline()).split()[1])
yllcorner = float((f.readline()).split()[1])
cellsize = float((f.readline()).split()[1])
NODATA = float((f.readline()).split()[1])

# read elevation data
z=[]
for line in f:
    line = line.strip()
    columns = line.split()
    z.append(columns)
f.close()

z=np.array(z,dtype="Float32")
z[z==NODATA]=0    # set absent values to 0 elevation

# construction northing/eastings grid
X=xllcorner+np.arange(np.size(z,1))*cellsize
Y=yllcorner+np.arange(np.size(z,0))*cellsize
Y=np.flip(Y,0)

# create triangular mesh (vertices are k1,k2,k3, vector nornal is norm) 
# and build and save as stl file
fileSTL = open(mapName+'_dem.stl', 'w')        
fileSTL.write('solid "dem"')

for y in np.arange(np.size(z,0)-1):
    for x in np.arange(np.size(z,1)-1):
        k1=np.array([X[x], Y[y], z[y,x]])
        k2=np.array([X[x], Y[y+1], z[y+1,x]])
        k3=np.array([X[x+1], Y[y], z[y,x+1]])
        norm=np.cross(k3-k2,k2-k1)
        
        fileSTL.write('\n  facet normal %s %s %s' % ((norm[0],norm[1],norm[2])))
        fileSTL.write('\n    outer loop ')
        fileSTL.write('\n      vertex %s %s %s' % ((k1[0],k1[1],k1[2])))
        fileSTL.write('\n      vertex %s %s %s' % ((k2[0],k2[1],k2[2])))
        fileSTL.write('\n      vertex %s %s %s' % ((k3[0],k3[1],k3[2])))
        fileSTL.write('\n    endloop ')
        fileSTL.write('\n  endfacet')
        
        k1=np.array([X[x], Y[y+1], z[y+1,x]])
        k2=np.array([X[x+1], Y[y+1], z[y+1,x+1]])
        k3=np.array([X[x+1], Y[y], z[y,x+1]])
        norm=np.cross(k3-k2,k2-k1)
        
        fileSTL.write('\n  facet normal %s %s %s' % ((norm[0],norm[1],norm[2])))
        fileSTL.write('\n    outer loop ')
        fileSTL.write('\n      vertex %s %s %s' % ((k1[0],k1[1],k1[2])))
        fileSTL.write('\n      vertex %s %s %s' % ((k2[0],k2[1],k2[2])))
        fileSTL.write('\n      vertex %s %s %s' % ((k3[0],k3[1],k3[2])))
        fileSTL.write('\n    endloop ')
        fileSTL.write('\n  endfacet')


fileSTL.write('\nendsolid "dem"')
fileSTL.close()
