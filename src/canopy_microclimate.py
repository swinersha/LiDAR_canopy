# This package hosts analyses to investigate sub-canopy microclimate based on the
# vertical distribution of leaf area within the canopy.

import numpy as np

# Estimate distribution of light within canopy with a given LAD, assuming the
# assumption of horizontal homogeneity.
# Light transmittance at any point in a continuous vertical column of voxels to
# a canopy level, j=v, is given by:
#     I_v = I_0*exp(-k*sum(LAD[j=v:-1]))
# k is the extinction coefficient defining Beer-Lambert-like decay of light
# irradiance through the canopy
# I_0 is the incident radiation at the top of the canopy.  If I_0==1 this will
# give the fraction of light transmitted to a given canopy layer.
# For reference - see Stark et al., Ecology Letters, 2012.  In this paper, they
# use k=0.034
def estimate_canopy_light_transmittance(LAD,heights,k,I_0=1):
    # make sure that canopy levels are labelled from ground up.
    if heights[0]>heights[1]:
        LAD = LAD[::-1]

    N_levels = heights.size
    dz = np.abs(heights[1]-heights[0])
    I = I_0*np.exp( -k*np.cumsum(LAD[::-1])[::-1]*dz )

    return I

# Estimate fraction of light absorbed at each layer within the canopy assuming
# Beer-Lambert decay of light intensity into canopy with horizontally uniform
# LAD distributions
def estimate_canopy_light_absorption(I,k):
    N_levels = I.size
    temp_I = np.zeros(N_levels+1)
    temp_I[1:] = I.copy()
    temp_I[0] = I[0]
    I0 = I[-1]
    A = (temp_I[1:]-temp_I[:-1])/I0

    return A
