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
data_shape = bold.shape
voxel_shape = data_shape[0:3]
voxel_index_grid = list(np.ndindex(voxel_shape))

data = bold.get_fdata() #
voxel_timecourse = data[20, 30, 30, :] # Nifti1Image -> Numpy array (example for time series of voxel at 20, 30, 30)

anat = nib.load('subj1/anat.nii.gz')
labels = pd.read_csv('subj1/labels.txt', sep=' ')

def get_bold_in_roi(bold, roi_mask=nib.load('subj1/mask4_vt.nii.gz')):

    return bold.get_fdata()[roi_mask.get_fdata() == 1, :]

# Plot anatomy
#plotting.plot_anat(anat)

# Plot data using a "glass brain"
#some_data = bold.slicer[:, :, :, 0]  # First BOLD image
#plotting.plot_glass_brain(some_data)



def searchlight(center_voxels, radius, search_grid):
    """This is a searchlight function that returns an array for each center voxel corresponding to
    all search_grid locations that are within radius (euclidean distance) from the center voxel

    Parameters
    ----------
    center_voxels : list
        a list or array of voxel locations around which seearch is performed
    radius: float
        search radius: locations within this radius from each center voxel are included in return
    search_grid: array
        3D array of all possible locations

    Returns
    -------
    dict
        dictionary of lists, where each key is a center voxel and items are lists of locations inside
        the search radius from that center voxel

    """
    search_results = {}
    for center_voxel in center_voxels:
        distances = scipy.spatial.distance.cdist(search_grid, np.array([center_voxel]))
        found_locations = np.array(search_grid)[distances.flatten() <= radius]
        search_results[center_voxel] = found_locations

    return search_results
