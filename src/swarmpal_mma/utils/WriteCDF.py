#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 10:51:08 2025

@author: ngp
"""

import chaosmagpy as cp
from datetime import datetime as dt
import os


from utils.Coord_Trans import RM
from utils.Coord_Trans import rotate_gauss
# from Coord_Trans import get_MagLat

pwd = os.getcwd()


# def writeCDF_gauss(timeL2,qsL2,ghL2,paramsL2,qsMSERL2,ghMSERL2,timeL3,qsL3,\
#                    ghL3,paramsL3,qsMSERL3,ghMSERL3):
def WriteCDF(ds_mma, params,OutputDir=pwd):
    from spacepy import pycdf
    # os.chdir(WORK_DIR)
    
    '''
    Construct the file name based on beginning and end time
    '''
    pre='SW_TEST_SHA_MMA_2E_' 
    su='_0101.cdf'
    #time=cp.data_utils.timestamp(ds_mma.time).astype(dt)
    time=ds_mma.time
    # tini=min(timeL2[0],timeL3[0])
    # tfin=max(timeL2[-1],timeL3[-1])
    tini=time[0]
    tfin=time[-1]
    t0=tini.strftime('%Y%m%dT%H%M%S')
    tf=tfin.strftime('%Y%m%dT%H%M%S')
    
    DT_folder=str(int(params.dt)).zfill(2)+'h-kernel'
    folder=os.path.join(OutputDir,DT_folder)
    if not os.path.exists(folder):
           os.makedirs(folder)
    
    filename = os.path.join(folder, pre + t0 + '_' + tf + su)
    
    print('Writing to file '+filename)
    
    '''
    Create a new file
    '''
    if os.path.exists(filename):
        os.remove(filename)
    
    cdf = pycdf.CDF(filename, '')
    
    cdf.attrs['Author'] = 'British Geological Survey'
    cdf.attrs['CreateDate'] = dt.now()
    cdf.attrs['TITLE'] = 'ESA Swarm L2 Extended Magnetospheric Model (MMA_SHA_2E)'

    '''
    Calculate the rotation matrix to be applied
    it chooses the time in the middle of the dataset and 
    applies spacepy core model to find the magnetic pole.
    '''
    Ms=RM(time,from_str='GEO',to_str='SM')
    gh_SM=rotate_gauss(ds_mma.gh,time,params,Ms=Ms)
    qs_SM=rotate_gauss(ds_mma.qs,time,params,Ms=Ms)
    
    
    '''
    Write variables to cdf
    '''
    cdf['Epoch'] = time
    
    cdf['nm']=[params.ns,params.ms]
   
    """
    External coefficients
    """
    cdf['qs_GEO'] = ds_mma.qs
    cdf['qs_GEO'].attrs['units'] = 'nT'
    cdf['qs_SM'] = qs_SM
    cdf['qs_SM'].attrs['units'] = 'nT'
    cdf['qs_RMSE'] = ds_mma.MSER_e**0.5
    cdf['qs_RMSE'].attrs['units'] = 'nT'
    
    """
    Internal coefficients
    """
    cdf['gh_GEO'] = ds_mma.gh
    cdf['gh_GEO'].attrs['units'] = 'nT'
    cdf['gh_SM'] = gh_SM
    cdf['gh_SM'].attrs['units'] = 'nT'
    cdf['gh_RMSE'] = ds_mma.MSER_i**0.5
    cdf['gh_RMSE'].attrs['units'] = 'nT'
    
    
    cdf.close()    

