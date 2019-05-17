#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 12:47:12 2019

extract all building shapes as stl files from ARCGIS scene layer package archive.

file format specification
input: .slpk (https://docs.opengeospatial.org/cs/17-014r5/17-014r5.html#78)
output: .stl (ASCII STL https://en.wikipedia.org/wiki/STL_(file_format))

default output coordinates are northings/eastings. Set X0,Y0 to centre locally

Test data is '3D Wellington' database: https://www.arcgis.com/home/item.html?id=9c39b3bcc9d24358a89c20fcffd909b7


@author: Sean
"""
import json
import struct
import numpy as np
from pyproj import Proj, transform
import os
import gzip
from pyunpack import Archive

# extract files from archive
archiveName = raw_input("\nEnter archive name (excl .slpk extension): ")
Archive(archiveName+'.slpk').extractall(archiveName,auto_create_dir=True)
       
## map projections. 
outProj = Proj(init='epsg:2193') # norths/easts
inProj = Proj(init='epsg:4326') # lat/lon

## center coordinates. Adjust to centre locally 
X0=0
Y0=0

# loop through all buildings in archive
for aa in os.listdir(archiveName+'/nodes/'):
    try:
        dirname=archiveName+'/nodes/'+str(aa)
        filename=dirname+'/geometries/0.bin.gz'
        
        # get reference position (nodes are given as offsets from here)
        jsondata=gzip.open(dirname+'/3dNodeIndexDocument.json.gz') 
        nodedata= json.loads(jsondata.read(-1))
        [x0,y0,z0,h0]=nodedata.get('mbs')
        
        # get building number (should match arcgis browser building id)
        featuresdata=gzip.open(dirname+'/features/0.json.gz')
        featuredata= json.loads(featuresdata.read(-1))
        building_id=featuredata['featureData'][0].get('id')
        
        savename='building_'+str(building_id)
        
        # read birary file with node locations (X,Y,Z) and normal vectors (Xn, Yn, Zn)
        file_length_in_bytes = os.path.getsize(filename)
        with gzip.open(filename, mode='rb') as file: 
            fileContent = file.read()
            size=int(struct.unpack("i",fileContent[0:4])[0])
            A= struct.unpack("f"*size*3, fileContent[8:8+size*12])
            An= struct.unpack("f"*size*3, fileContent[8+size*12:8+size*24])
        
            # convert lat/lon offsets to absolute
            X=np.array(A[0::3])+x0
            Y=np.array(A[1::3])+y0
            
            #transform lat/lon into N/E
            X,Y = transform(inProj,outProj,X,Y)
            X=np.array(X,dtype='float32')
            Y=np.array(Y,dtype='float32')
            
            # output on local ref scale
            X=X-X0
            Y=Y-Y0
        
            Z=np.array(A[2::3])+z0
            Z=np.array(Z,dtype='float32')
        
            Xn=np.array(An[0::3],dtype='float32')
            Yn=np.array(An[1::3],dtype='float32')
            Zn=np.array(An[2::3],dtype='float32')
            
                
            # build into vector arrays
            V=np.asarray([X,Y,Z]).T
            Vn=np.asarray([Xn,Yn,Zn]).T
                
            #build STL file
            fileSTL = open(archiveName+'/'+savename+'.stl', 'w')        
            fileSTL.write('\nsolid "%s"' % (savename))
            for idx, norm in enumerate(Vn[0::3,:]):
                fileSTL.write('\n  facet normal %s %s %s' % ((norm[0],norm[1],norm[2])))
                fileSTL.write('\n    outer loop ')
                fileSTL.write('\n      vertex %s %s %s' % ((V[idx*3,0],V[idx*3,1],V[idx*3,2])))
                fileSTL.write('\n      vertex %s %s %s' % ((V[idx*3+1,0],V[idx*3+1,1],V[idx*3+1,2])))
                fileSTL.write('\n      vertex %s %s %s' % ((V[idx*3+2,0],V[idx*3+2,1],V[idx*3+2,2])))
                fileSTL.write('\n    endloop ')
                fileSTL.write('\n  endfacet')
            fileSTL.write('\nendsolid "%s"' % (savename))
            fileSTL.close()
    
    except:
        print("Error for file %s - is this junk data?" %(aa))