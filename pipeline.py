"""
Script for analysing which areas of the brain are activated when identifying different pictures.
NOTE: This script is an exercise version and should NOT be used in actual analysis.
STATUS: Currently DRAFT for analysing a single subject.
"""

import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy.spatial.distance import pdist, squareform
from progress.bar import Bar
from nilearn import plotting



def preprocess_chunk(chunk_data):
    """This function preprocesses a chunk of data by first removing linear trend and the
    z-scoring the data. Operations are performed on the last axis in data.

    Parameters
    ----------
    chunk_data : array-like
        NOTE: operations will be performed on the last axis.

    Returns
    -------
    array-like
        A preprocessed version of chunk data in same shape and format"""

    detrended = scipy.signal.detrend(chunk_data)
    z_scored = scipy.stats.zscore(detrended, axis=-1)

    return z_scored

def preprocess_voxel_data(bold_data, labels):
    """Wrapper for handling preprocessing for a whole dataset comprised of chunks.

    Parameters
    ----------
    bold_data : array-like
        (NumPy) array containing neural image data

    labels : Pandas dataframe
        Should contain at least columns 'chunks' that matches in length to bold_data. This chunk information
        is used to split bold_data into chunks, each pre-processed separately.

    Returns
    -------
    array-like
        A chunk-wise preprocessed version of bold_data in same shape and format
    """


    processed_bold_np = np.zeros(bold_data.shape)
    chunks = np.unique(labels.chunks)

    chunk_bar = Bar('Preprosessing chunks', max=len(chunks))
    for chunk in chunks:
        labels_chunk = labels.query(f'chunks == {chunk}')
        bold_chunk = bold_data[:, :, :, labels_chunk.index]
        preprocessed_chunk = preprocess_chunk(bold_chunk)
        processed_bold_np[:, :, :, labels_chunk.index] = preprocessed_chunk
        chunk_bar.next()

    chunk_bar.finish()
    return processed_bold_np

def get_bold_in_roi(bold, roi_mask=nib.load('subj1/mask4_vt.nii.gz')):

    return bold.get_fdata()[roi_mask.get_fdata() == 1, :]

# Plot anatomy
#plotting.plot_anat(anat)


def searchlight(center_voxels, radius, search_grid):
    """This is a searchlight function that returns an array for each center voxel corresponding to
    all search_grid locations that are within radius (euclidean distance) from the center voxel

    Parameters
    ----------
    center_voxels : list
        a list or array of voxel locations around which seearch is performed
    radius: float
        search radius: locations within this radius from each center voxel are included in return
    search_grid: list
        all possible locations in 3D coordinates, in list format

    Returns
    -------
    dict
        dictionary of lists, where each key is a center voxel and items are lists of locations inside
        the search radius from that center voxel in 2D array format: line is a voxel, columns are coordinates.

    """
    search_results = {}
    for center_voxel in center_voxels:
        distances = scipy.spatial.distance.cdist(search_grid, np.array([center_voxel]))
        found_locations = np.array(search_grid)[distances.flatten() <= radius]
        search_results[center_voxel] = found_locations


    return search_results


def build_model_RDM(labels):

    model_RDM = np.zeros((len(labels.index), len(labels.index)))
    labels_sorted = labels.sort_values('labels')



def remove_rest(data, labels):
    """Removes 'rest' labeled data.

    Parameters
    ----------
    data : array-like
        data to be cleaned

    labels : Pandas dataframe
        labels corresponding to last axis in data

    Returns
    -------
    array-like
        data that has been cleaned of data corresponding to 'rest' labels

    Pandas dataframe
        labels that correspond to returned data

    """

    clean_data = data[:, :, :, labels.query('labels != "rest" ').index]
    clean_labels = labels[labels.labels != 'rest']

    return clean_data, clean_labels

def create_model_RDM(labels):
    model_RDM = np.zeros((len(labels.index), len(labels.index)))

    for i in range(len(labels.labels)):
        for j in range(len(labels.labels)):
            model_RDM[i, j] = (labels.labels.iloc[i] == labels.labels.iloc[j])

    return model_RDM


def flatten_voxels(data, locations, image):
    flat = np.array([])
    for loc in locations:
        flat = np.append(flat, data[loc[0], loc[1], loc[2], image])

    return flat


def create_bold_RDM(data, location, ROI_searchlights):

    search_locs = ROI_searchlights[location]
    search_locs_data = np.array([data[loc[0], loc[1], loc[2], :].flatten() for loc in search_locs]).T
    RDM = squareform(pdist(search_locs_data, metric='correlation'))

    return RDM

# Input params
radius = 2 # radius for searchlight

# Load original data
bold = nib.load('subj1/bold.nii.gz') # loads dataset of BOLD images in Nifti1Image format
mask = nib.load('subj1/mask4_vt.nii.gz')
anat = nib.load('subj1/anat.nii.gz')
labels = pd.read_csv('subj1/labels.txt', sep=' ')

data = bold.get_fdata()
mask_data = mask.get_fdata()

# Preprocessing
print("Pre-processing...")
processed_bold_data = preprocess_voxel_data(data, labels)
preprocessed_image = nib.Nifti1Image(processed_bold_data, bold.affine)

# Remove 'rest' images from data
# TODO: find correct place to apply this
#pic_voxels, pic_labels = remove_rest(processed_bold_data, labels)

# Sort everything according to labels
print("Sorting...")
labels_sorted = labels.sort_values('labels')
voxels_sorted = processed_bold_data[:, :, :, labels.index]

# create voxel index
print("Creating voxel index...")
data_shape = voxels_sorted.shape
voxel_shape = data_shape[0:3]
voxel_index_grid = list(np.ndindex(voxel_shape))

# Create list of ROI voxel locations:
ROI_locs = list(map(tuple, np.argwhere(mask_data == 1)))

# Create searchlight areas for each ROI location
print("Creating searchlights")
ROI_searchlights = searchlight(ROI_locs, radius, voxel_index_grid)

# create BOLD RDMs for all center voxels:
ROI_RDMs = {}
ROI_RDM_progress_bar = Bar('Computing RDMs for ROIs', max=len(ROI_locs))

for loc in ROI_locs:

    ROI_RDMs[loc] = create_bold_RDM(data, loc, ROI_searchlights)
    ROI_RDM_progress_bar.next()

ROI_RDM_progress_bar.finish()

# TODO: Check that RDMs are OK! (plot something)