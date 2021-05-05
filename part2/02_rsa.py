"""
Perform RSA analysis using a searchlight approach.

Author: Marijn van Vliet <marijn.vanvliet@aalto.fi>
"""
import argparse

# Basic scientific libs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Some algorithms we will need
from scipy.spatial import distance
from scipy.stats import spearmanr

# Neuroscience packages for loading and visualizing data
import nibabel as nib
from nilearn import plotting

# Nice progress bar
from tqdm import tqdm

# Sibling modules
import config
import viz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, help='The subject to process')
args = parser.parse_args()

# Load preprocessed fMRI data
bold = nib.load(config.output_data_path / f'subj{args.subject}' / 'bold_preprocessed.nii.gz')

# Load preprocessed metadata
meta = pd.read_csv(config.output_data_path / f'subj{args.subject}' / 'labels_preprocessed.txt', sep=' ')

# This is a mask that the authors provide. It is a GLM contrast based
# localizer map that extracts an ROI in the "ventral temporal" region.
roi_mask = nib.load(config.input_data_path / f'subj{args.subject}' / 'mask4_vt.nii.gz')

# Create the model RDM
print('Computing model RDM...')
rdm_model = distance.pdist(meta[['labels']], lambda a, b: a != b)
np.savez(config.output_data_path / f'subj{args.subject}' / 'rdm_model.npz', rdm_model)

# Collect the RSA results here
rsa_result = np.zeros(bold.shape[:3])  # result has no time dimension

# Create (i, j, k) indices corresponding to all the voxels in the MRI image
all_voxels = np.array(list(np.ndindex(bold.shape[:3])))

# Select all voxels that are part of the ROI
roi_voxels = roi_mask.get_fdata().nonzero()
roi_voxels = np.array(roi_voxels).T

# Create searchlight patches
pbar = tqdm('Searchlight', total=len(roi_voxels), unit='patches')
for center_voxel in roi_voxels:
    # `cdist` wants both inputs to be lists, so we need to wrap
    # center_voxel in a list and unwrap the result.
    dist_to_center = distance.cdist([center_voxel], all_voxels)[0]
    patch = all_voxels[dist_to_center <= config.searchlight_radius]

    # NumPy fancy indexing requires tuples
    patch_data = bold.get_fdata()[tuple(patch.T)]
    center_voxel = tuple(center_voxel)

    rdm_patch = distance.pdist(patch_data.T, metric='correlation')
    rsa_result[center_voxel], _ = spearmanr(rdm_model, rdm_patch)

    pbar.update(1)
pbar.close()

# Packing the results in a Nifti1Image makes for easy saving and plotting
rsa_result = nib.Nifti1Image(rsa_result, bold.affine, bold.header)

# Save the result
output_dir = config.output_data_path / f'subj{args.subject}'
output_dir.mkdir(parents=True, exist_ok=True)
nib.save(rsa_result, output_dir / 'rsa_result.nii.gz')

# Plot the result.
fig_dir = config.figure_path / f'subj{args.subject}'
fig_dir.mkdir(parents=True, exist_ok=True)
viz.plot_rdm(rdm_model, meta.labels, title='Model RDM', output_file=fig_dir / 'model_rdm.pdf')
plotting.plot_glass_brain(rsa_result)
plt.savefig(fig_dir / 'rsa.pdf')
