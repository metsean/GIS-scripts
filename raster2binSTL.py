#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:20:40 2019

Converts raster (tif) elevation map to binary stl
- run in same directory as tif file
- prompts for x,y scale if not provided (checks for tfw extension).
- origin at 0,0
- tri surface is basic grid of triangles
- uses libtiff to read tiff file and stl package to generate norms and save file

Tested on LINZ 8m topo https://data.linz.govt.nz/layer/51768-nz-8m-digital-elevation-model-2012/)
Generates big files!

@author: Sean
"""

import numpy as np
from stl import mesh
from libtiff import TIFF

#inRaster = "DEM_BN32_2013_1000_4046.tif"
#inRaster='TARAS-25pc.tif'
inRaster = raw_input("\nEnter raster dem file name (incl tif extension): ")

baseName = inRaster.split('.')[0]
outSTL = baseName + ".stl"

# check for dem scale
try :
    f=open(baseName+'.tfw','r')
    scale=float(f.readline())
except:
    scale=float(raw_input("\nEnter dem scale (in meters): "))

# open raster
tif = TIFF.open(inRaster, mode='r')
imarray = tif.read_image()

# stl indexing is backwards
z=np.flip(imarray,0)

# reset no values
z[z==-32767]=0
#z=z[:3,:2]

# define sampling pattern for tri surface
y=np.arange((np.size(z,0)))
x=np.arange((np.size(z,1)))

ypat=np.array([0,0,1,1,0,1])
samy=(y.reshape((len(y),1))[:-1]+np.tile(ypat,len(x)-1)).flatten()

xpat=np.array([0, 1, 0, 0, 1, 1])
samx=np.tile((x[:-1]+xpat.reshape(6,1)).T.flatten(),len(y)-1)


#sample topo array to create trisurface
data = np.zeros(len(samy)/3, dtype=mesh.Mesh.dtype)
data['vectors']=np.array([samx*scale,samy*scale,z[samy,samx]]).T.reshape((len(samy)/3,3,3))

your_mesh = mesh.Mesh(data)
your_mesh.save(outSTL,update_normals=True)
