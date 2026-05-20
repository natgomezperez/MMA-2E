        
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 14:51:27 2024

@author: ngp
"""
'''
Usage:
im=maps(clm,fig,ax,ll='SM',lmax=lmax,vi=vi,cm=cm,lim=lim,cobar=False

set up a map axis as:
fig, axes = plt.subplots(subplot_kw={'projection':ccrs.EqualEarth(180)},
                      figsize=(5,3))


INPUT:

    clm     array of the gauss coefficients
    fig     figure handle
    ax      axis to use
    ll      coordinate system, use 'SM' in solar magnetic
    lmax    is the max degree in the array clm
    vi      is the component you want to plot vi could be 'rad', 'theta','phi', 'total','horz'
    cm      is the colormap cm='viridis'
    lim     is defined if you want to set the limits in the colormap, do not defined to select limits automatically
    cobar   boolean variable to plot a color bar

'''


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import xarray as xr


import pyshtools as pysh
import cartopy.crs as ccrs
#from cartopy.util import add_cyclic_point
from matplotlib.patches import Rectangle
# from cartopy.feature.nightshade import Nightshade

RE=6.371e6

def list2matrix(clm,lmax):
    coeffs = np.zeros((2, lmax+1, lmax+1))
    j=0
    for l in range(1,lmax+1):
         coeffs[0,l,0]=clm[j]
         j=j+1
         for m in range(1,l+1):
             coeffs[0,l,m]=clm[j]
             coeffs[1,l,m]=clm[j+1]
             
             j=j+2
    return coeffs

def myround(x, base=10,up=1):
    return base * (round(x/base)+ up)


def map_surface_rtp(ext,fig=False,ax=False,ll='',field='',cm='seismic',lmax=3,vi='rad',lim=0,cobar=True):

    coeffs= list2matrix(ext,lmax)
    cilm=pysh.SHMagCoeffs.from_array(coeffs,r0=RE,csphase=-1) 
    grid = cilm.expand(lmax_calc=lmax,lmax=15)
    
    if vi=='theta':
        data=grid.theta.to_xarray()
        field='{\\theta}'
        cl=1
    elif vi=='rad':
        data=grid.rad.to_xarray()
        field='r'
        cl=-1
    elif vi=='phi':
        data=grid.phi.to_xarray()
        field='{\\phi}'
        cl=-1
    elif vi=='total':
        data=grid.total.to_xarray()
        field='T'
        cl=1        
    elif vi=='horz':
        data=np.sqrt((grid.phi.to_xarray())**2+(grid.theta.to_xarray())**2)
        field='H'
        cl=1
    
    

    if lim==0:
        lim=max(myround(data.max().values),myround(abs(data.min().values)))
        lev=np.arange(-lim, lim+0.1, lim/10)
    else:
        if cl==-1:
            lev=np.arange(-lim, lim+0.1, lim/5)
        elif cl==1:
#            lim=myround(data.max().values)
            lev=np.arange(0, lim+0.1, lim/10)

    if not(fig) or not(ax):
        fig = plt.figure(figsize=(10, 3))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.EqualEarth(180))



    img=ax.contourf(data.lon, data.lat, data.values,levels=lev,
                transform=ccrs.PlateCarree(),
                cmap=cm)
    if len(lev)<10:
        ax.contour(data.lon, data.lat, data.values,levels=lev,
                transform=ccrs.PlateCarree())#,

    ax.add_patch(patches.Rectangle(xy=[270, -90], width=90, height=180,
                                   linewidth=0,
                                   fill=True,
                                   fc='w',
                                   alpha=0.5,
                                   zorder=10,
                                   hatch='///',
                                   transform=ccrs.PlateCarree())
                 )
    ax.add_patch(patches.Rectangle(xy=[0, -90], width=90, height=180,
                                   linewidth=0,
                                   fill=True,
                                   fc='w',
                                   alpha=0.5,
                                   zorder=10,
                                   hatch='///',
                                   transform=ccrs.PlateCarree())
                 )

    if cobar:
        cbar=fig.colorbar(img,ax=ax, ticks=[lev[0],0,lev[-1]])
        cbar.set_label(r'$B_'+field+'$ (nT)')

    ax.set_global()

    return img  
    



def _subsolar_longitude(hour):
    """
    Subsolar longitude in degrees east.
    Assumes t is UTC (naive datetime, Greenwich).
    """
    #hour = t.hour + t.minute / 60.0 + t.second / 3600.0

    # Earth rotates 15° per hour relative to the Sun
    lon = 180.0 - 15.041067 * hour

    # Wrap to [-180, 180]
    return ((lon + 180) % 360) - 180

def _getfield_from_grid(ext,lmax,vi):

    coeffs= list2matrix(ext,lmax)
    cilm=pysh.SHMagCoeffs.from_array(coeffs,r0=RE,csphase=-1) 
    grid = cilm.expand(lmax_calc=lmax,lmax=15)

    if vi=='theta':
        data=grid.theta.to_xarray()
        field='{\\theta}'
        cl=1
    elif vi=='rad':
        data=grid.rad.to_xarray()
        field='r'
        cl=-1
    elif vi=='phi':
        data=grid.phi.to_xarray()
        field='{\\phi}'
        cl=-1
    elif vi=='total':
        data=grid.total.to_xarray()
        field='T'
        cl=1        
    elif vi=='horz':
        data=np.sqrt((grid.phi.to_xarray())**2+(grid.theta.to_xarray())**2)
        field='H'
        cl=1
    return data,field,cl

def add_dayside_patches(ax, subsolar_lon, alpha=0.5):
    """
    Add dayside shading as two patches in geographic coordinates.
    Works correctly for rotated projections.
    """

    day_kwargs = dict(
        facecolor="white",
        alpha=alpha,
        edgecolor="none",
        transform=ccrs.PlateCarree(),
        zorder=2,
    )

    # Dayside spans ±90° around subsolar longitude
    lon1 = subsolar_lon - 90
    lon2 = subsolar_lon + 90

    # Wrap into [-180, 180]
    lon1 = ((lon1 + 180) % 360) - 180
    lon2 = ((lon2 + 180) % 360) - 180

    if lon1 < lon2:
        # Dayside does NOT cross dateline → single patch
        ax.add_patch(Rectangle(
            (lon1, -90),
            lon2 - lon1,
            180,
            **day_kwargs
        ))
    else:
        # Dayside crosses dateline → two patches
        ax.add_patch(Rectangle(
            (-180, -90),
            lon2 + 180,
            180,
            **day_kwargs
        ))
        ax.add_patch(Rectangle(
            (lon1, -90),
            180 - lon1,
            180,
            **day_kwargs
        ))


def _get_projection(name, central_longitude=0, central_latitude=0):
    name = name.lower()

    if name == "platecarree":
        return ccrs.PlateCarree(central_longitude=central_longitude)

    if name == "robinson":
        return ccrs.Robinson(central_longitude=central_longitude)

    if name == "mollweide":
        return ccrs.Mollweide(central_longitude=central_longitude)

    if name == "equalearth":
        return ccrs.EqualEarth(central_longitude=central_longitude)

    if name == "orthographic":
        return ccrs.Orthographic(
            central_longitude=central_longitude,
            central_latitude=central_latitude,
        )

    raise ValueError(f"Unknown projection: {name}")


def _apply_projection(ax, projection_name, *,
                     central_longitude=0, central_latitude=0):
    """
    Replace an existing Axes with a Cartopy GeoAxes
    in the SAME subplot position.

    Returns the new ax.
    """

    fig = ax.figure
    pos = ax.get_position()

    # Remove old axes
    fig.delaxes(ax)

    # Create new axes in same place
    proj = _get_projection(
        projection_name,
        central_longitude=central_longitude,
        central_latitude=central_latitude,
    )

    new_ax = fig.add_axes(pos, projection=proj)
    new_ax.set_global()

    return new_ax


def _gauss_to_map(gauss,vi,movie):
    ext=gauss.values[0]
    lmax=int(round(-3 + np.sqrt(1 + 8*len(ext))) / 4)+1 

#    t = pd.to_datetime(gauss["time"].item()).to_pydatetime()

#==================Make  th emovie here, calculate all frames here
    #data,field,cl=getfield_from_grid(ext,lmax,vi)
    
    map,field,cl=_getfield_from_grid(ext,lmax,vi)
    lat         = map.lat
    lon         = map.lon

    data = np.empty((gauss["time"].size, lat.size, lon.size))
    #pydt = np.empty((hour.size))


    data[0,:,:] = map.values


#    pydt[0] = pd.to_datetime(ext["time"].item()).to_pydatetime()


    if movie:
        for i, gauss_t in enumerate(gauss[1:]):
            
            map,_,_=_getfield_from_grid(gauss_t.values,lmax,vi)
 #           pydt[i] = pd.to_datetime(gauss["time"][0].item()).to_pydatetime()
            # compute spatial field
            data[i+1, :, :] = map.values
    
        

    ds_map = xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={
            "time": gauss["time"],
            "lat": lat,
            "lon": lon,
        },
        name=field,
    )

    return ds_map,cl,field


def map_gauss(gauss,ax=None,cm=None,
              vi='horz',cobar=True, movie=False,
              proj="platecarree"):
    """
    Plot a global surface centred on midnight.
    

    Parameters
    ----------
    gauss, an xarray with 
        values : gauss coefficient len(gauss.values)= (ℓmax​+1)(2ℓmax​+1)
        time:    xarray datetime coordinate
    cm: colormap
    vi: scalar field to plot options are
            'rad'
            'horiz'
            'total'
            'phi'
            'theta'
    cobar: logical value to plot a colorbar
    proj: desired projection, current values:
            "platecarree"
            "robinson"
            "equalearth"
            "orthographic"      

    """
    
    hour=gauss["time"].dt.hour.data +\
        gauss["time"].dt.minute.data / 60.0 + gauss["time"].dt.second.data / 3600.0

    
#==============================

    # values = data.values
    # lat    = data.lat
    # lon    = data.lon
    maps,cl,field=_gauss_to_map(gauss,vi,movie)
    lat    = maps["lat"]
    lon    = maps["lon"]

    if cm == None:
        if cl<0:
            cm='seismic'
        else:
            cm='viridis'



    # Midnight longitude = opposite the Sun
    subsolar_lon = _subsolar_longitude(hour)
    midnight_lon = ((subsolar_lon + 180) % 360)
    # if midnight_lon > 180:
    #     midnight_lon -= 360
    midnight_lon[midnight_lon > 180]= midnight_lon[midnight_lon > 180]- 360


    if ax==None:
    
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes()
    
        
    



    
    mask = (lat > -89.8) & (lat < 89.8)


    #for i,map in maps:
    for i, map in enumerate(maps):
        ax = _apply_projection(
            ax,
            proj,
            central_longitude=midnight_lon[i]
        )
        pcm = ax.contourf(
            lon,
            lat[mask],
            map.values[mask,:],
            transform=ccrs.PlateCarree(),
            cmap=cm,
        )
        
        t_str = pd.to_datetime(map["time"].item()).strftime("%Y-%m-%d %H:%M")



        ax.coastlines(color="black", linewidth=0.8, zorder=3)
        add_dayside_patches(ax, subsolar_lon[i])

        ax.set_global()

        #t_str = t.strftime("%Y-%m-%d %H:%M")
        ax.set_title(f"UTC "+t_str)

        if cobar:
            cbar=plt.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
            cbar.set_label(r'$B_'+field+'$ (nT)')
        
        plt.show()