#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:20:40 2019
-
Converts raster (tif) elevation map to binary stl
- run in same directory as tif file
- edit file to set local origin (X0,Y0)
- tri surface is basic grid of triangles
- uses rasterio to read tiff file and stl package to generate norms and save file

Tested on LINZ 8m topo https://data.linz.govt.nz/layer/51768-nz-8m-digital-elevation-model-2012/)
Generates big files!

@author: Sean
"""

import numpy as np
from stl import mesh
import rasterio
from pyproj import Proj, transform

def raster2bin():
    inRaster = input("\nEnter raster dem file name (incl tif extension): ")
    
    baseName = inRaster.split('.')[0]
    outSTL = baseName + ".stl"
    
    #import dem
    src = rasterio.open(inRaster) 
    imarray=src.read()
    z=imarray[0,:,:]
       
    # stl indexing is backwards
    z=np.flip(z,0)
     
    # reset no data values
    z[z==src.meta['nodata']]=0
    
    # get grid scale
    scale=src.meta['transform'][0] 
    
    # define sampling pattern for tri surface
    y=np.arange((np.size(z,0)))
    x=np.arange((np.size(z,1)))
    
    ypat=np.array([0,0,1,1,0,1])
    samy=(y.reshape((len(y),1))[:-1]+np.tile(ypat,len(x)-1)).flatten()
    
    xpat=np.array([0, 1, 0, 0, 1, 1])
    samx=np.tile((x[:-1]+xpat.reshape(6,1)).T.flatten(),len(y)-1)
    
    #sample raster array to create trisurface
    data = np.zeros(int(len(samy)/3), dtype=mesh.Mesh.dtype)
    
    #xy scale
    outProj = Proj(init='epsg:2193') # norths/easts
    inProj = Proj(init='epsg:4326') # lat/lon
    
    # define local coordiant centre  
    X0,Y0= transform(inProj,outProj,174.768296,-41.289659)
    
    x0=src.meta['transform'][2]-X0
    y0=src.meta['transform'][5]-src.meta['height']*src.meta['transform'][0]-Y0
    
    
    
    data['vectors']=np.array([(samx+1)*scale+x0,(samy+1)*scale+y0,z[samy,samx]]).T.reshape((int(len(samy)/3),3,3))
    your_mesh = mesh.Mesh(data) # update normals implicit here
    your_mesh.save(outSTL,update_normals=False)
    

raster2bin()