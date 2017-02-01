import numpy as np

# Load spreadsheet of LAI derived from hemispherical photographs (courtesy of Terhi Riutta at Oxford).  LAI estimated using Hemisfer.
def load_field_LAI(LAI_file):
    datatype = {'names': ('ForestType','Plot', 'Subplot', 'LAI'), 'formats': ('S32','S32','i8','f16')}
    hemisfer_LAI = np.genfromtxt(LAI_file, skiprows = 1, delimiter = ',',dtype=datatype)

    return hemisfer_LAI


# This function loads the subplot coordinates from a csv file.  File columns should be as follows:
# Plot Subplot 'X0', 'Y0', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3'
def load_boundaries(coordinate_list):
    
    datatype = {'names': ('Plot', 'Subplot', 'X0', 'Y0', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3'), 'formats': ('S32','i8','f16','f16','f16','f16','f16','f16','f16','f16')}
    coords = np.genfromtxt(coordinate_list, skiprows = 1, delimiter = ',',dtype=datatype)
    plot_name=np.unique(coords['Plot'])
    coordinate_dict = {}
    subplot_dict = {}
    for pp in range(0,plot_name.size):
        n_subplots = np.sum(coords['Plot']==plot_name[pp])
        subplot_polygons = np.zeros((n_subplots,5,2))
        subplot_list = np.zeros(n_subplots)
        for i in range(0,n_subplots):
            subplot_polygons[i,0,0]=coords['X0'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,0,1]=coords['Y0'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,1,0]=coords['X1'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,1,1]=coords['Y1'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,2,0]=coords['X2'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,2,1]=coords['Y2'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,3,0]=coords['X3'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,3,1]=coords['Y3'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,4,0]=coords['X0'][coords['Plot']==plot_name[pp]][i]
            subplot_polygons[i,4,1]=coords['Y0'][coords['Plot']==plot_name[pp]][i]
            subplot_list[i]=coords['Subplot'][coords['Plot']==plot_name[pp]][i]
        coordinate_dict[plot_name[pp]]=subplot_polygons.copy()
        subplot_dict[plot_name[pp]]=subplot_list.copy()
    return coordinate_dict, subplot_dict

# get bounding box for list of coordinates
def get_bounding_box(coordinate_list):
    N = coordinate_list.shape[0]
    bbox = np.zeros((4,2))
    top = coordinate_list[:,1].max()
    bottom = coordinate_list[:,1].min()
    left = coordinate_list[:,0].min()
    right = coordinate_list[:,0].max()
    bbox[0,0]=left
    bbox[0,1]=top
    bbox[1,0]=right
    bbox[1,1]=top
    bbox[2,0]=right
    bbox[2,1]=bottom
    bbox[3,0]=left
    bbox[3,1]=bottom
    return bbox