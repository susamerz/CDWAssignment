# %%
import pandas as pd
import numpy as np

from nilearn import plotting
import nibabel as nib

from scipy import signal, stats

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

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


def create_selection_mask(bold, x:int=None,y:int=None,z:int=None, r:int=None):
    """Create mask for the BOLD image based on user input.

    if any of the values are non-int, no mask will be created.
    
    Parameters
    ----------
    bold: array_like
        target data for masking. This variable is used to get the dimensions.

    x: int, optional
        x dimension

    y: int, optional
        y dimension

    z: int, optional
        z dimension

    r: int, optional
        radius of selection.

    Returns
    -------
    ret : array_like
        returns a list of indicies if validation is true
    """
    
    if any(list(map(lambda m: m is None, [x,y,z]))) :
        warnings.warn('inputs contain None. No selection applied')
        return(np.ones(bold.shape[:3])) # no mask

    else:

        if r is not None:

            # creating distance matrix
            i,j,k = np.indices(bold.shape[:3], sparse=True)
            distmat = np.sqrt((i-x)**2 + (j-y)**2 + (k-z)**2)

            # creating the mask based on distance
            mask_cube =np.zeros(bold.shape[:3])
            mask_cube[distmat<= r] = 1
            return(mask_cube == 1)

        else:

            return(np.ones(bold.shape[:3])) # no mask


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
        The input data

    labeled_df : Pandas DataFrame
        The labels data

    Returns
    -------
    
    """
    label_image_count = labeled_df.groupby('labels').count().values[0,0]
    labels_count = len(labeled_df['labels'].unique())


    bold_array_masked = bold_array_masked.reshape(-1,bold_array_masked.shape[-1])
    label_sorting = labeled_df.sort_values('labels').index

    print('preparing RDMs')

    dis_matrix=1-np.corrcoef(bold_array_masked[:,label_sorting].T)


    model_RDM = np.kron(
        (1-np.eye(labels_count)), 
        np.ones((label_image_count,label_image_count)))
        
    RSA_score = np.corrcoef(model_RDM.T.flatten(),dis_matrix.flatten())

    print('Plotting the results')

    
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

    print(f'RSA score is : {round(RSA_score[0,1],5)}')




#%%

# Dir Config
data_dir = ''

bold_dta_path = 'subj1/bold.nii.gz'
mask_path = 'subj1/mask4_vt.nii.gz'
label_path = 'subj1/labels.txt'


## Starting the analysis process:

# data preparation
bold = nib.load(data_dir + bold_dta_path)

labeled_df = pd.read_csv(data_dir + label_path, sep=' ')
labeled_df = labeled_df[~labeled_df.labels.isin(['rest','scrambledpix'])]

chunks_df = labeled_df.reset_index()\
    .groupby(['chunks'])\
    .agg({'index':list})

bold_array = bold.get_fdata().copy()
bold_array = standardize_data(bold_array, chunks_df['index'])


# User inputs:
X = 20
Y = 12
Z = 40
RADIUS = 10

images = [400]

mask_cube = create_selection_mask(bold_array, x=X, y=Y, z=Z, r=RADIUS)

# Plotting the MRI image:
fig, ax = plt.subplots(nrows = len(images))


for i,image_index in enumerate(images):
    temp = bold_array[:,:,:,image_index].copy()
    temp[~mask_cube] = 0
    processed_image = nib.Nifti1Image(temp, bold.affine)

    if len(images) == 1:
        axes = ax
    else:
        axes = ax[i]

    plotting.plot_glass_brain(processed_image,title=str(image_index), axes =axes)

# Producing RDM and RSA:
bold_array_masked = bold_array
bold_array_masked[~mask_cube] = 0


RSA_RDM_producer(bold_array_masked, labeled_df)


# %%
