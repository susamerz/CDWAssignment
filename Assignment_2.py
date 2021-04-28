# %%
import pandas as pd
import numpy as np

from nilearn import plotting
import nibabel as nib

from scipy import signal, stats

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

import glob
import warnings
# %%

def standardize_data(bold_data, chunks):

    """Standardizes and detrends the data.
    
    Parameters
    ----------
    bold_data : array_like 
        4-D array with time dimension on last index The input data
    
    chunks_df : array_like
        array containing the indicies of chenks ordered by their time

    Returns
    -------
    temp : ndarray
        z-score of the input data.
    
    """
    for chunk in chunks:
        bold_data[:,:,:,chunk] = \
            stats.zscore(\
            signal.detrend(\
                bold_data[:,:,:,chunk],type='linear'))
    
    return(bold_data)

def plot_MRI(image,bold,mask,title=None, ax=None):
    """gets the input and produces searchlight mask if applicable.
    
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


def RSA_RDM_producer(bold_array_masked, labeled_df):
    """Produces RDM and Model RDM and plots them.
    
    Parameters
    ----------
    bold_array_masked : array_like
        The input data, masked and flattened

    labeled_df : Pandas DataFrame
        The labels data

    Returns
    -------
    
    """
    label_image_count = labeled_df.groupby('labels').count().values[0,0]
    labels_count = len(labeled_df['labels'].unique())
    label_sorting = labeled_df.sort_values('labels').index

    dis_matrix=1-np.corrcoef(bold_array_masked[:,label_sorting].T)

    model_RDM = np.kron(
        (1-np.eye(labels_count)), 
        np.ones((label_image_count,label_image_count)))
        
    RSA_score = np.corrcoef(model_RDM.T.flatten(),dis_matrix.flatten())[0,1]
    
    fig, ax = plt.subplots()
    im = plt.imshow(dis_matrix, cmap='PiYG')

    cax = plt.axes([0.8, 0.12, 0.03, 0.78])
    plt.colorbar(im,cax=cax)
    ticks = ((label_image_count * np.arange(labels_count)) + label_image_count/2)
    tick_labels = labeled_df.sort_values('labels')['labels'].unique()
                    
    ax.hlines(label_image_count * np.arange(labels_count),\
        *ax.get_xlim(), color='w')

    ax.vlines(label_image_count * np.arange(labels_count),\
        *ax.get_xlim(), color='w')

    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))

    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FixedFormatter(tick_labels))
    plt.title('RDM vs RDM')

    print(f'RSA score is : {round(RSA_score,5)}')
    return(RSA_score)


def plot_MRIs(images:list, bold_array, bold, mask_cube):
    """Plots MRI images from input data
    
    Parameters
    ----------
    images : array_like
        The selected images from subjects

    bold_array : 4-D array_like
        The BOLD array that is prepared

    bold : nibabel.nifti1.Nifti1Image
        nibabel image for producing MRI plot

    mask_cube : 3-D boolean array
        mask array to plot only selected area.

    Returns
    -------
    temp : 3-D np.darray
        Average of images.

    """

    fig, ax = plt.subplots(nrows = len(images))

    average_of_images = []
    for i,image_index in enumerate(images):
        temp = bold_array[:,:,:,image_index].copy()
        temp[~mask_cube] = 0
        processed_image = nib.Nifti1Image(temp, bold.affine)
        plotting.plot_glass_brain(processed_image)

        if len(images) == 1:
            axes = ax
            return(temp) # return for grand average
        else:
            axes = ax[i]
            average_of_images.append(temp)

    temp = np.array(average_of_images).mean(axis=0) # returning average images
    return(temp)
#%%
################ MAIN OPERATIONS! #############################################

# ----------------- USER PARAMETERS ----------------------------------------- #

# Dir Config

subjects_data_dir = 'subjects'

# user selection:

# images that are chosen to visualized.
# keep one image for averaging out!
images = [400] 

use_spotlight = False # if false, no need to define the rest

X = 20
Y = 12
Z = 40
RADIUS = 10

# ----------------- local variables operations ------------------------------ #

list_of_BOLDs_path = glob.glob(subjects_data_dir + '/*/bold*.gz')
list_of_MASKs_path = glob.glob(subjects_data_dir + '/*/mask4*.gz')
list_of_labels_path = glob.glob(subjects_data_dir + '/*/labels*')
  
# ----------------- Analysis and plots  ------------------------------------- #

list_of_RSA = []
average_MRI_list = []
pass_first_load = True

for bold, mask, label in zip(list_of_BOLDs_path, list_of_MASKs_path,list_of_labels_path):
    print(bold)
    print(mask)
    print(label)

    labeled_df = pd.read_csv(label, sep=' ')
    labeled_df = labeled_df[~labeled_df.labels.isin(['rest','scrambledpix'])]
    chunks_df = labeled_df.reset_index()\
        .groupby(['chunks'])\
        .agg({'index':list})

    mask_cube = nib.load(mask).get_fdata() == 1
    bold = nib.load(bold)
    bold_array = bold.get_fdata()
    pass_first_load = False


    # applying mask to reduce calculations.
    # dimentions are preserved in this form
    bold_array[~mask_cube] = 0 

    bold_array = standardize_data(bold_array, chunks_df['index'])
    average_MRI_list.append(plot_MRIs(images, bold_array, bold, mask_cube))

    # input array is flattened and the masked data is dropped
    list_of_RSA.append(RSA_RDM_producer(bold_array[mask_cube,:], labeled_df))
    print('\n')

print(f'Average RSA is : {np.array(list_of_RSA).mean()}')

average_MRI_list = np.array(average_MRI_list).mean(axis=0)
average_MRI_list[~mask_cube] = 0
processed_image = nib.Nifti1Image(average_MRI_list, bold.affine)
plotting.plot_glass_brain(processed_image,title='grand average')
# %%