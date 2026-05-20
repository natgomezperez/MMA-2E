#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 13:17:39 2025

@author: ngp

coord=0 Solar magnetic
coord=1 = GEOC

"""

# import xarray as xr
from spacepy import pycdf
import numpy as np
import pandas as pd
import os
import glob


#InDir='/users/ngp/QMatrix/data/2025'



def Read_MMAcdf(file,coord=0):
    
    
    if coord==0:
        cco='SM'
    elif coord==1:
        cco='GEO'
            
    cdf=pycdf.CDF(file)

    time=cdf['Epoch'][...]
    qs=cdf['qs_'+cco][...]
    gh=cdf['gh_'+cco][...]
    qsMSER3=cdf['qs_RMSE'][...]
    ghMSER3=cdf['gh_RMSE'][...]

    d=np.column_stack((time,qs,gh,qsMSER3,ghMSER3))

    #Make the headings for the columns
    lmax=cdf['nm'][...][0,-1]
    qs_columns=[]
    gh_columns=[]
    count=0
    for n in range(1,lmax+1):
        for m in range(min(lmax,n)+1):
            qs_columns.append('q'+str(n)+str(m))
            gh_columns.append('g'+str(n)+str(m))
            count=count+1
            if m!=0:
                qs_columns.append('s'+str(n)+str(m))
                gh_columns.append('h'+str(n)+str(m))
                count=count+1
    cols=['time']
    cols.extend(qs_columns)
    cols.extend(gh_columns)
    cols.extend(['qsMSER','ghMSER'])
    
    return pd.DataFrame(data=d,columns=cols,index=time)

def Read_all(delt=8,coord=0):
    
    # os.chdir(InDir)
    DT_folder=str(int(delt)).zfill(2)+'h-kernel'
    path=os.path.join(InDir,DT_folder)
    list_of_files = glob.glob(os.path.join(path,'SW_TEST_SHA_MMA_2E*.cdf')) 
    
    dfall= pd.DataFrame()
    for file in list_of_files:
        dfall=pd.concat([dfall,
                         Read_MMAcdf(file,coord)])
    return dfall.sort_values(by=['time']).drop_duplicates('time', keep='last')

