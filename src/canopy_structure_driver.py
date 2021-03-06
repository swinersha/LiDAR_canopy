###############################################################################################################
# This driver function analyses both LiDAR data and field inventory data to produce independent estimates of
# canopy structure.  These are compared against each other and their integrated LAD is compared against LAI
# estimates from hemispherical photographs.
# An additional test is to change the vertical resolution to investigate whether this improves the stability of
# the LAD profiles when the point cloud becomes sparse - for example lower in the canopy of old growth forest
############################################################################################################### 
import numpy as np
import sys
from matplotlib import pyplot as plt
import LiDAR_tools as lidar
import auxilliary_functions as aux
import LiDAR_MacHorn_LAD_profiles as LAD1
import LiDAR_radiative_transfer_LAD_profiles as LAD2
import structural_metrics as structure
import plot_LAD_profiles as plot_LAD

# start by defining input files
las_file = 'Carbon_plot_point_cloud_buffer.las'
subplot_coordinate_file = 'BALI_subplot_coordinates_corrected.csv'

# also define output directory (for saving figures)
output_dir = './Figures/'
pointcloud_dir = './subplot_pointclouds/'

# define important parameters for canopy profile estimation
Plots = ['LF','E','Belian','Seraya','B North','B South','DC1','DC2']
#Plots = ['Belian']
N_plots = len(Plots)
leaf_angle_dist = 'spherical'
max_height = 80
max_return = 3
layer_thickness = 1
layer_thickness_2m = 2
#layer_thickness_5m = 5
n_layers = np.ceil(max_height/layer_thickness)
minimum_height = 2.

# define dictionaries to host the various canopy profiles and LAI estimates that will be produced
MacArthurHorn_LAD = {}
radiative_DTM_LAD = {}
MacArthurHorn_LAD_2m = {}
#MacArthurHorn_LAD_5m = {}
#radiative_LAD_5m = {}
radiative_LAD_2m = {}
#radiative_LAD_noS = {}
# load coordinates and lidar points for target areas
subplot_polygons, subplot_labels = aux.load_boundaries(subplot_coordinate_file)
all_lidar_pts = lidar.load_lidar_data(las_file)

# loop through all plots to be analysed
for pp in range(0,N_plots):
    print Plots[pp]
    Plot_name=Plots[pp]
    # clip LiDAR point cloud to plot level (this makes subsequent processing much faster)
    n_coord_pairs = subplot_polygons[Plot_name].shape[0]*subplot_polygons[Plot_name].shape[1]
    coord_pairs = subplot_polygons[Plot_name].reshape(n_coord_pairs,2)
    bbox_polygon = aux.get_bounding_box(coord_pairs)
    plot_lidar_pts = lidar.filter_lidar_data_by_polygon(all_lidar_pts,bbox_polygon)
    
    # get some subplot-level information
    n_subplots = subplot_polygons[Plot_name].shape[0]

    # set up some arrays to host the radiative transfer based profiles
    heights_rad = np.arange(0,max_height+1)
    heights_rad_2m = np.arange(0,max_height+1,2.)
    #heights_rad_5m = np.arange(0,max_height+1,5.)
    LAD_rad_DTM = np.zeros((n_subplots,heights_rad.size,max_return))
    LAD_rad_2m = np.zeros((n_subplots,heights_rad_2m.size,max_return))
    #LAD_rad_5m = np.zeros((n_subplots,heights_rad_5m.size,max_return))
    #LAD_rad_2m_noS  = np.zeros((n_subplots,heights_rad_2m.size,max_return))

    # set up some arrays to host the MacArthur-Horn profiles
    heights = np.arange(0,max_height)+1
    heights_2m = np.arange(0,max_height,2.)+2
    #heights_5m = np.arange(0,max_height,5.)+5
    LAD_MH = np.zeros((n_subplots, heights.size))
    LAD_MH_2m = np.zeros((n_subplots, heights_2m.size))
    #LAD_MH_5m = np.zeros((n_subplots,heights_5m.size))
    
    """
    # write point cloud to file for testing
    out = open(pointcloud_dir + Plot_name+'_pts.csv','w')
    out.write('x,y,z,plot,subplot\n')
    """
    # loop through subplots, calculating both return profiles and LAD distributions
    for i in range(0,n_subplots):
        print "Subplot: ", subplot_labels[Plot_name][i]
        subplot_index = subplot_labels[Plot_name][i]-1 # this is so that the subplots are stored in a logical order
        # filter lidar points into subplot
        sp_pts = lidar.filter_lidar_data_by_polygon(plot_lidar_pts,subplot_polygons[Plot_name][i,:,:])
        """
        for p in range(0,sp_pts.shape[0]):
            out.write(str(sp_pts[p,0]) + ',' + str(sp_pts[p,1]) + ',' + str(sp_pts[p,2]) + ',' +  Plot_name + ',' + str(subplot_labels[Plot_name][i])+'\n')

    out.close()
        """


        # first of all, loop through the return numbers to calculate the radiative LAD profiles, accounting for imperfect penetration of LiDAR pulses into canopy
        for rr in range(0,max_return):
            max_k=rr+1
            u,n,I,U = LAD2.calculate_LAD_DTM(sp_pts,heights_rad,max_k,'spherical')
            LAD_rad_DTM[subplot_index,:,rr]=u[::-1].copy()
            u,n,I,U = LAD2.calculate_LAD_DTM(sp_pts,heights_rad_2m,max_k,'spherical')
            LAD_rad_2m[subplot_index,:,rr]=u[::-1].copy()
            #u,n,I,U = LAD2.calculate_LAD_DTM(sp_pts,heights_rad_5m,max_k,'spherical')
            #LAD_rad_5m[i,:,rr]=u[::-1].copy()


            #sp_pts_noS = sp_pts.copy()
            #sp_pts_noS[:,5] = 0
            #u,n,I,U = LAD2.calculate_LAD_DTM(sp_pts_noS,heights_rad_2m,max_k,'spherical')
            #LAD_rad_2m_noS[i,:,rr]=u[::-1].copy()

        # now get MacArthur-Horn profiles
        heights,first_return_profile,n_ground_returns = LAD1.bin_returns(sp_pts, max_height, layer_thickness)
        LAD_MH[subplot_index,:] = LAD1.estimate_LAD_MacArtherHorn(first_return_profile, n_ground_returns, layer_thickness, 1.)
        heights_2m,first_return_profile,n_ground_returns = LAD1.bin_returns(sp_pts, max_height, layer_thickness_2m)
        LAD_MH_2m[subplot_index,:] = LAD1.estimate_LAD_MacArtherHorn(first_return_profile, n_ground_returns, layer_thickness_2m, 1.)
        #heights_5m,first_return_profile,n_ground_returns = LAD1.bin_returns(sp_pts, max_height, layer_thickness_5m)
        #LAD_MH_5m[i,:] = LAD1.estimate_LAD_MacArtherHorn(first_return_profile, n_ground_returns, layer_thickness_5m, 1.)

    # now we have looped through and created the different profiles, need to account for any NaN's and apply minimum height
    # to the LAD distributions
    # - set NaN values to zero
    LAD_rad_DTM[np.isnan(LAD_rad_DTM)]=0
    LAD_MH[np.isnan(LAD_MH)]=0
    LAD_rad_2m[np.isnan(LAD_rad_2m)]=0
    LAD_MH_2m[np.isnan(LAD_MH_2m)]=0
    #LAD_rad_5m[np.isnan(LAD_rad_5m)]=0
    #LAD_MH_5m[np.isnan(LAD_MH_5m)]=0
    # - remove all profile values below minimum height prior to comparison
    mask = heights <= minimum_height
    LAD_MH[:,mask]=0
    #mask = np.max(heights_rad)-heights_rad<=minimum_height
    mask = heights_rad<=minimum_height
    LAD_rad_DTM[:,mask]=0
    mask = heights_2m <= minimum_height
    LAD_MH_2m[:,mask]=0
    mask = heights_rad_2m<=minimum_height
    LAD_rad_2m[:,mask]=0
    #LAD_MH_5m[:,0]=np.nan
    #LAD_rad_5m[:,:2]=np.nan

    # Store arrays into respective dictionaries
    MacArthurHorn_LAD[Plot_name] = LAD_MH.copy()
    radiative_DTM_LAD[Plot_name] = LAD_rad_DTM.copy()
    MacArthurHorn_LAD_2m[Plot_name] = LAD_MH_2m.copy()
    #MacArthurHorn_LAD_5m[Plot_name] = LAD_MH_5m.copy()
    radiative_LAD_2m[Plot_name] = LAD_rad_2m.copy()
    #radiative_LAD_5m[Plot_name] = LAD_rad_5m.copy()

    #radiative_LAD_noS[Plot_name] = LAD_rad_2m_noS.copy()

# write profiles to file# save profiles for plot to file
OutFile = '/home/dmilodow/DataStore_DTM/BALI/LiDAR/src/output/BALI_subplot_LAD_profiles_MacHorn_1m'
np.savez(OutFile+'.npz', **MacArthurHorn_LAD)
OutFile = '/home/dmilodow/DataStore_DTM/BALI/LiDAR/src/output/BALI_subplot_LAD_profiles_MacHorn_2m'
np.savez(OutFile+'.npz', **MacArthurHorn_LAD_2m)
OutFile = '/home/dmilodow/DataStore_DTM/BALI/LiDAR/src/output/BALI_subplot_LAD_profiles_RadiativeTransfer_1m'
np.savez(OutFile+'.npz', **radiative_DTM_LAD)
OutFile = '/home/dmilodow/DataStore_DTM/BALI/LiDAR/src/output/BALI_subplot_LAD_profiles_RadiativeTransfer_2m'
np.savez(OutFile+'.npz', **radiative_LAD_2m)




# Plot up the subplot profiles to see how changing resolution impacts on the resultant LAD profiles
for pp in range(0,N_plots):
    print Plots[pp]
    label_string = Plots[pp]
    figure_name = output_dir + '/subplot_profiles/'+Plots[pp]+'_subplot_LAD_profiles_MH_1m'
    plot_LAD.plot_subplot_LAD_profiles(MacArthurHorn_LAD[Plots[pp]],heights,'g',label_string,figure_name)

    figure_name = output_dir + '/subplot_profiles/'+Plots[pp]+'_subplot_LAD_profiles_MH_2m'
    plot_LAD.plot_subplot_LAD_profiles(MacArthurHorn_LAD_2m[Plots[pp]],heights_2m,'g',label_string,figure_name)

    figure_name = output_dir + '/subplot_profiles/'+Plots[pp]+'_subplot_LAD_profiles_rad_1m_k2'
    plot_LAD.plot_subplot_LAD_profiles(radiative_DTM_LAD[Plots[pp]][:,:,1],heights_rad,'g',label_string,figure_name)

    figure_name = output_dir + '/subplot_profiles/'+Plots[pp]+'_subplot_LAD_profiles_rad_1m_k3'
    plot_LAD.plot_subplot_LAD_profiles(radiative_DTM_LAD[Plots[pp]][:,:,2],heights_rad,'g',label_string,figure_name)

    figure_name = output_dir + '/subplot_profiles/'+Plots[pp]+'_subplot_LAD_profiles_rad_2m_k2'
    plot_LAD.plot_subplot_LAD_profiles(radiative_LAD_2m[Plots[pp]][:,:,1],heights_rad_2m,'g',label_string,figure_name)

    figure_name = output_dir + '/subplot_profiles/'+Plots[pp]+'_subplot_LAD_profiles_rad_2m_k3'
    plot_LAD.plot_subplot_LAD_profiles(radiative_LAD_2m[Plots[pp]][:,:,2],heights_rad_2m,'g',label_string,figure_name)



# next step is to take the canopy profiles and get the vertical and horizontal canopy structural metrics
# use the 2m profiles - both radiative transfer and MacArthur-Horn versions for comparison

# Load previously saved canopy profiles
InFile = '/home/dmilodow/DataStore_DTM/BALI/LiDAR/src/output/BALI_subplot_LAD_profiles_MacHorn_1m.npz'
MacArthurHorn_LAD = np.load(InFile)

peaks= {}
sp_peaks = {}
vertical_structural_variance = {}
frechet_dist = {}
Sh_v_1ha = {}
Sh_h_1ha = {}
Sh_v = {}
filter_window = 9.
threshold = 0.05

for pp in range(0,N_plots):
    print Plots[pp]
    plot_name = Plots[pp]
    print "\t- getting vertical metrics"
    peak_heights, subplot = structure.retrieve_peaks_gaussian_convolution(MacArthurHorn_LAD[plot_name],heights,sigma=2,plot_profiles=False)
    peaks[plot_name] = peak_heights.size/25.                                           
    # get variance in layer heights
    vertical_structural_variance[plot_name] = structure.calculate_vertical_structural_variance(peak_heights)

    # get Shannon index
    Sh_v_1ha[plot_name] = structure.calculate_Shannon_index(np.mean(MacArthurHorn_LAD[plot_name],axis=0))
    Sh_h_1ha[plot_name] = structure.calculate_Shannon_index(np.sum(MacArthurHorn_LAD[plot_name],axis=1))
    subplot_shannon = np.zeros(25)
    subplot_peaks = np.zeros(25)
    for ss in range(0,25):
        subplot_shannon[ss]=structure.calculate_Shannon_index(MacArthurHorn_LAD[plot_name][ss,:])
        subplot_peaks[ss] = peak_heights[subplot==ss].size
    Sh_v[plot_name]=subplot_shannon.copy()
    sp_peaks[plot_name]= subplot_peaks.copy()


colour = ['#46E900','#1A2BCE','#E0007F']
rgb = [[70,233,0],[26,43,206],[224,0,127]]
labels = ['$1^{st}$', '$2^{nd}$', '$3^{rd}$', '$4^{th}$']



"""
peaks_MH = {}
peaks_MH_2m = {}
vertical_structural_variance_MH = {}
peaks_rad = {}
peaks_rad_2m = {}
vertical_structural_variance_rad = {}
filter_window = 9.
filter_order = 4
threshold = 0.05

for pp in range(0,N_plots):
    print Plots[pp]
    plot_name = Plots[pp]
    print "\t- getting vertical metrics"
    peak_heights_MH = structure.retrieve_peaks_gaussian_convolution(MacArthurHorn_LAD[plot_name],heights,sigma=2,plot_profiles=True)
    peak_heights_rad = structure.retrieve_peaks_gaussian_convolution(radiative_DTM_LAD[plot_name][:,:,-1],heights_rad,sigma=2,plot_profiles=False)
    peak_heights_MH_2m = structure.retrieve_peaks_gaussian_convolution(MacArthurHorn_LAD_2m[plot_name],heights_2m)
    peak_heights_rad_2m = structure.retrieve_peaks_gaussian_convolution(radiative_LAD_2m[plot_name][:,:,-1],heights_rad_2m)
    peaks_MH[plot_name] = peak_heights_MH.size
    peaks_rad[plot_name] = peak_heights_rad.size
    peaks_MH_2m[plot_name] = peak_heights_MH.size
    peaks_rad_2m[plot_name] = peak_heights_rad.size
    # get variance in layer heights
    vertical_structural_variance_MH[plot_name] = structure.calculate_vertical_structural_variance(peak_heights_MH)
    vertical_structural_variance_rad[plot_name] = structure.calculate_vertical_structural_variance(peak_heights_rad)
"""

"""

# first up - create some dictionaries to host the structural metrics
frechet_dist_MH = {}
peaks_MH = {}
vertical_structural_variance_MH = {}
VSI_MH = {}
frechet_dist_rad = {}
peaks_rad = {}
vertical_structural_variance_rad = {}
VSI_rad = {}

for pp in range(0,N_plots):
    print Plots[pp]
    plot_name = Plots[pp]
    # get peaks
    print "\t- getting vertical metrics"
    peak_heights_MH = structure.retrieve_peaks(MacArthurHorn_LAD[plot_name],heights)
    peak_heights_rad = structure.retrieve_peaks(radiative_DTM_LAD[plot_name][:,:,-1],heights_rad)
    peaks_MH[plot_name] = peak_heights_MH.size
    peaks_rad[plot_name] = peak_heights_rad.size
    # get variance in layer heights
    vertical_structural_variance_MH[plot_name] = structure.calculate_vertical_structural_variance(peak_heights_MH)
    vertical_structural_variance_rad[plot_name] = structure.calculate_vertical_structural_variance(peak_heights_rad)
    # get VSI
    VSI_MH[plot_name] = structure.calculate_VSI(peak_heights_MH)
    VSI_rad[plot_name] = structure.calculate_VSI(peak_heights_rad)
    print "\t- getting horizontal metrics"
    # get mean Frechet distance
    frechet_dist_MH[plot_name] = structure.calculate_mean_Frechet_distance(MacArthurHorn_LAD[plot_name],heights)
    frechet_dist_rad[plot_name] = structure.calculate_mean_Frechet_distance(radiative_DTM_LAD[plot_name][:,:,-1],heights_rad)
"""


sys.path.append('/home/dmilodow/DataStore_DTM/USEFUL_PYTHON_STUFF/generic_plotting/src/')
import violin_plot as plt2

# Fourth violin plots of LAI Mac-Horn and LAI-hemisfer

colors = [ '#45E900','#45E900','#45E900','#45E900','#1A2CCE','#1A2CCE','#E0007F','#E0007F']

plt.figure(4, facecolor='White',figsize=[4,4])
#ax1 = plt.subplot2grid((2,1),(0,0))
ax1 = plt.subplot2grid((1,1),(0,0))
#ax2 = plt.subplot2grid((2,1),(1,0),sharex=ax1)
#x_offs = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5]   
x_offs = [5.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0]

for pp in range(0,N_plots):
    plt2.violin_plot(ax1,Sh_v[plot[pp]],color=colors[pp],alpha='0.8',x_offset=x_offs[pp])
    #plt2.violin_plot(ax1,sp_peaks[plot[pp]],color=colors[pp],alpha='0.8',x_offset=x_offs[pp])
    
# configure plot
#ax1.annotate('a - Number of canopy layers', xy=(0.05,0.95), xycoords='axes fraction',horizontalalignment='left', verticalalignment='top', fontsize=rcParams['font.size']+2,backgroundcolor='white') 
ax1.annotate('Canopy Shannon diversity index', xy=(0.05,0.95), xycoords='axes fraction',horizontalalignment='left', verticalalignment='top', fontsize=rcParams['font.size']+2,backgroundcolor='white') 

#ax1.set_ylabel('Number of layers',fontsize=axis_size)
ax1.set_ylabel('Shannon index',fontsize=axis_size)

x_locs = x_offs
ax1.set_xticks(x_locs)
xticks=ax1.get_xticks().tolist()
xticks[0]='Belian'
xticks[1]='Seraya'
xticks[2]='DC1'
xticks[3]='DC2'
xticks[4]='E'
xticks[5]='LF'
xticks[6]='B North'
xticks[7]='B South'
ax1.set_xticklabels(xticks,rotation=90,fontsize=axis_size)
ax1.set_ylim(ymax=4.5)
#ax2.set_xticklabels(xticks,rotation=90,fontsize=axis_size)

#xticklabels = ax1.get_xticklabels()
#plt.setp(xticklabels,visible=False)

plt.subplots_adjust(hspace=0.001,wspace=0.001)

plt.tight_layout()
plt.savefig('Vertical_structural_diversity_metrics.png')


plt.show()
                             
