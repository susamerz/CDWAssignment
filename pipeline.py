"""
Script for analysing which areas of the brain are activated when identifying different pictures.
NOTE: This script is an exercise version and should NOT be used in actual analysis.
STATUS: Currently DRAFT for analysing a single subject.
"""

import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from nilearn import plotting


bold = nib.load('subj1/bold.nii.gz') # loads dataset of BOLD images in Nifti1Image format
mask = nib.load('subj1/mask4_vt.nii.gz')
data_shape = bold.shape
voxel_shape = data_shape[0:3]
voxel_index_grid = list(np.ndindex(voxel_shape))

data = bold.get_fdata() #
voxel_timecourse = data[20, 30, 30, :] # Nifti1Image -> Numpy array (example for time series of voxel at 20, 30, 30)

anat = nib.load('subj1/anat.nii.gz')
labels = pd.read_csv('subj1/labels.txt', sep=' ')

def preprocess_chunk(chunk_data):

    print(chunk_data[0:3, 0:3, 0:3, 0:10])
    detrended = scipy.signal.detrend(chunk_data)
    z_scored = scipy.stats.zscore(detrended, axis=-1)
    print(z_scored[0:3, 0:3, 0:3, 0:10])

    return z_scored

def preprocess_voxel_data(bold_data, labels):

    processed_bold_np = np.zeros(bold_data.shape)
    chunks = np.unique(labels.chunks)
    for chunk in chunks:
        labels_chunk = labels.query(f'chunks == {chunk}')
        bold_chunk = bold_data[:, :, :, labels_chunk.index]
        preprocessed_chunk = preprocess_chunk(bold_chunk)
        processed_bold_np[:, :, :, labels_chunk.index] = preprocessed_chunk

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

# Plot data using a "glass brain"
#some_data = bold.slicer[:, :, :, 0]  # First BOLD image
#plotting.plot_glass_brain(some_data)


#voxels_in_roi = data[mask.get_fdata() == 1, :]
#filter = mask.get_fdata() == 1

processed_bold_data = preprocess_voxel_data(data, labels)
print(processed_bold_data[0:3, 0:3, 0:3, 0:10])
preprocessed_image = nib.Nifti1Image(processed_bold_data, bold.affine)
#nib.save(preprocessed_image, 'images/preprocessed_img_subj1.nii.gz')
slice = preprocessed_image.slicer[:, :, :, 0]
plotting.plot_glass_brain(slice)
