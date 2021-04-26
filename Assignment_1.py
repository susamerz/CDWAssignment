# %%
import pandas as pd
import numpy as np

from nilearn import plotting
import nibabel as nib
from requests import ReadTimeout

from scipy import signal, stats

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

import warnings
# %%

def standardize_data(dta):

    """
    Standardizes and detrends the data
    
    Parameters
    ----------
    dta : array_like
        The input data
    
    Returns
    -------
    temp : ndarray
        z-score of the input data.
    
    """
    ret = stats.zscore(\
        np.round(\
            signal.detrend(dta,type='linear'),decimals = 6)
        )
    
    return(ret)

def RDM_plotter(matrix, ax,cmap = 'hot'):
    """
    Gets matplotlib.pyplot.axes, numpy 2-D matrix.
    then add plot to the axes
    
    Parameters
    ----------
    matrix : array_like
        The input data
    
    ax : matplotlib.pyplot.axes
        The input axes
        
    Returns
    -------
    im : matplotlib.image.AxesImage
        Produced heatmap
    
    """
    ticks = ((108 * np.arange(7)) + 54)
    tick_labels = labeled_df.sort_values('labels')['labels'].unique()
                    
    im = ax.imshow(matrix, cmap=cmap)
    ax.autoscale(False)
    ax.hlines(108 * np.arange(7), *ax.get_xlim(), color='w')
    ax.vlines(108 * np.arange(7), *ax.get_xlim(), color='w')
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))

    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FixedFormatter(tick_labels))
    return im

def distmat(image, index):
    """
    Gets one voxel and the image. Returns distance 
    from selected voxel from rest of the cells
    
    Parameters
    ----------
    image : array_like
        The input image
    
    index : array_like with image dimensions
        selected voxel 
        
    Returns
    -------
    ret : array_like
        returns an array with distance from index
    """
    i,j,k = np.indices(image.shape, sparse=True)
    ret = np.sqrt((i-index[0])**2 + (j-index[1])**2 + (k-index[1])**2)
    return(ret)

def create_selection(x=None,y=None,z=None):
    """
    Validates the input coordinates for Voxel
    
    Parameters
    ----------
    x: int
    
    y: int
    
    z: int
        
    Returns
    -------
    ret : array_like
        returns a list of indicies if validation is true
    """
    
    
    
    if not any(list(map(lambda k: k is None, [x,y,z,None]))):
        print('selection contains Non. No selection applied')
        return(None)
    elif all(list(map(lambda k: isinstance(k,int),[x,y,z]))):
        return([x,y,z])
    
    else:
        warnings.warn('selection coordinates is not int. No selection applied')
        return(None)

def bold_mask(bold:np.ndarray,voxel:list = None, r:int = None):
    
    """
    gets the input and produces searchlight mask if applicable.
    
    Parameters
    ----------
    bold: np.ndarray
        4-D array of the bold 
    selected: list
    
    r: int
        
    Returns
    -------
    ret : array_like
        returns the mask for searchlight
    """

    if (r is None) and (voxel is None):
        print('no selection is provided.')
        mask_cube =np.ones(bold.shape[:3])
        
    if (r is None) or (voxel is None):
        mask_cube =np.ones(bold.shape[:3])
        warning.warn('Both selection parameters should be defined. \
\nNo filter is applied')

    else:
        mask_cube =np.zeros(bold.shape[:3])
        mask_cube[distmat(mask_cube,voxel) <= r] = 1
        mask_cube = mask_cube == 1
    return(mask_cube)

def plot_MRI(image,bold,mask,title=None, ax=None):
    """
    gets the input and produces searchlight mask if applicable.
    
    Parameters
    ----------
    images: int
    index of the desired image
    bold: nibabel.nifti1.Nifti1Image
        BOLD image data
    mask: array_like
        Mask that is created to cover unnecessary data
        
    Returns
    -------
        MRI plots
    """
    processed_image = nib.Nifti1Image(image, bold.affine)
    # Now we can plot it
    plotting.plot_glass_brain(processed_image,title=title, axes =ax)

# %%
### THESE ARE PARAMETERS FOR THE MAIN FUNCTION!
# main function will be created after I understood what should I do :D 
#VARIABLES:




#%%

# Dir Config
data_dir = ''

bold_dta_path = 'subj1/bold.nii.gz'
mask_path = 'subj1/mask4_vt.nii.gz'
label_path = 'subj1/labels.txt'

## Starting the analysis process:

# data preparation
bold = nib.load(data_dir + bold_dta_path)
mask = nib.load(data_dir + mask_path)
labeled_df = pd.read_csv(data_dir + label_path, sep=' ')
labeled_df = labeled_df[~labeled_df.labels.isin(['rest','scrambledpix'])]
chunks = labeled_df.reset_index()\
    .groupby(['chunks'])\
    .agg({'index':list}).reset_index()
#%%

# User inputs:
x = 20
y = 30
z = 30
r = 10

images = [400,600,800]


selection = create_selection(x=x,y=y,z=z)
mask_cube = bold_mask(bold = bold.get_fdata(), voxel=selection, r=r)
bold_array = bold.get_fdata().copy()
bold_array[~mask_cube] = 0

for chunk in range(len(chunks)):
    bold_array[:,:,:,chunks.loc[chunk,'index']] = \
        standardize_data(bold_array[:,:,:,chunks.loc[chunk,'index']])

# RDM analysis process



bold_array_flatten = bold_array[mask_cube,:]

label_sorting = labeled_df.sort_values('labels').index
dis_matrix=1-pd.DataFrame(bold_array_flatten[:,label_sorting]).corr('pearson').values

# this two parameters shoudl be obtained from BOLD data
model_RDM = np.kron((1-np.eye(7)), np.ones((108,108)))
simi_matrix = np.corrcoef(model_RDM,dis_matrix)[756:,:756]

# Plotting the results

fig, ax = plt.subplots(ncols = 2, figsize=(11,5),
                    gridspec_kw=dict(width_ratios=[1,1]))

fig.subplots_adjust(wspace=0.5)
im1 = RDM_plotter(dis_matrix, ax[0],cmap = 'PiYG')
im2 = RDM_plotter(simi_matrix, ax[1], cmap = 'Purples')

cax = plt.axes([0.915, 0.12, 0.03, 0.78])
plt.colorbar(im2,cax=cax)
cax2 = plt.axes([0.45, 0.12, 0.03, 0.78])
plt.colorbar(im1,cax=cax2)

fig, ax = plt.subplots(nrows = len(images), figsize=(11,10))

for i,image_index in enumerate(images):
    plot_MRI(image= bold_array[:,:,:,image_index], bold = bold, mask = mask_cube,
             title = image_index, ax = ax[i])


# %%
