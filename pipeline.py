"""
Script for analysing which areas of the brain are activated when identifying different pictures.
NOTE: This script is an exercise version and should NOT be used in actual analysis.
STATUS: Currently DRAFT for analysing a single subject.
"""

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import plotting
from tools import *  # make sure namespace doesn't get messed up!
from matplotlib.pyplot import matshow, savefig

# Input params
searchlight_radius = 2

# Load original data
bold = nib.load('subj1/bold.nii.gz') # loads dataset of BOLD images in Nifti1Image format
mask = nib.load('subj1/mask4_vt.nii.gz')
anat = nib.load('subj1/anat.nii.gz')
labels = pd.read_csv('subj1/labels.txt', sep=' ')

data = bold.get_fdata()
mask_data = mask.get_fdata()

# Preprocessing
print("Pre-processing...")
chunk_id = labels.chunks.to_numpy()
processed_bold_data = preprocess_bold_data(data, chunk_id)
preprocessed_image = nib.Nifti1Image(processed_bold_data, bold.affine)

# Remove unwanted images from data
pic_voxels, pic_labels = remove_rows(processed_bold_data, labels, ['rest', 'scrambled pix'])

print("Sorting...")
labels_sorted = pic_labels.sort_values('labels')
voxels_sorted = pic_voxels[:, :, :, pic_labels.index]

# create voxel index
print("Creating voxel index...")
data_shape = voxels_sorted.shape
voxel_shape = data_shape[0:3]
voxel_index_grid = list(np.ndindex(voxel_shape))


# Create Model RDM
print("Creating model RDM")
model_RDM = create_model_RDM(labels_sorted.labels.to_numpy())
model_RDM_pic = matshow(model_RDM)
savefig("model_RDM.png")

# Create list of ROI voxel locations:
ROI_locs = list(map(tuple, np.argwhere(mask_data == 1)))


# create BOLD RDMs for all center voxels:
ROI_RSAs  ={}
ROI_RDM_progress_bar = Bar('Computing RDMs for ROIs', max=len(ROI_locs))

for loc in ROI_locs:

    ROI_RDM = create_bold_RDM(voxels_sorted, loc, searchlight_radius, voxel_index_grid)
    ROI_RSAs[loc], RSAp = spearmanr(ROI_RDM.flatten(), model_RDM.flatten())
    if np.isnan(ROI_RSAs[loc]):
        print(ROI_RDM)
        print("RSA value was nan")
        raise ValueError
        break
    ROI_RDM_progress_bar.next()

ROI_RDM_progress_bar.finish()


# create an RSA image:
print("Creating a Nifti1Image")
plot_data = np.zeros(data.shape[0:3])
for ROI_loc in ROI_RSAs:
    plot_data[ROI_loc] = ROI_RSAs[ROI_loc]

print("Plotting RSA figures")
img = nib.Nifti1Image(plot_data, bold.affine)
#plotting.plot_glass_brain(img, output_file="RSA_plot.png")
plotting.plot_glass_brain(img, output_file="RSA_plot_glass_brain.png")