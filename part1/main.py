# encoding: utf8
"""
Script that performs an example RSA analysis on the Haxby et al. (2001) dataset [1].
The data can be downloaded from: http://dev.pymvpa.org/datadb/haxby2001.html

References
----------
[1] Haxby, J., Gobbini, M., Furey, M., Ishai, A., Schouten, J., and Pietrini, P.
    (2001). Distributed and overlapping representations of faces and objects in
    ventral temporal cortex. Science 293, 2425-2430.

Author: Marijn van Vliet <marijn.vanvliet@aalto.fi>
"""
from pathlib import Path

# Basic scientific packages
import numpy as np
import pandas as pd

# Some algorithms we will need
from scipy.spatial import distance
from scipy.stats import spearmanr

# Neuroscience packages for loading and plotting data
from nilearn import plotting
import nibabel as nib

# Sibling modules
import preprocessing
import viz
import searchlight

subject = 1  # For now, we only have one subject
data_path = Path(f'../data/subj{subject}')  # The location of the data
result_fname = Path('rsa_result.nii.gz')  # The file to write the result to

# Load fMRI data
bold = nib.load(data_path / 'bold.nii.gz')

# This is the metadata of the experiment. What stimulus was shown when etc.
meta = pd.read_csv(data_path / 'labels.txt', sep=' ')

## Detrend and z-score data by chunk.
# Ok, here we go! First we will pre-process the data a little. "Chunks" are
# recording sessions between which the subject took a short break. I see in
# most example pipelines on the Haxby2001 data that they treat each chunk
# separately during detrending, so we will do the same here.
bold = preprocessing.preprocess(bold, chunks=meta.chunks, overwrite_data=True)

## Drop classes and sort images by class.
# We must ensure that all times, the metadata and the bold images are in sync.
# Hence, we first perform the operations on the `meta` pandas DataFrame. Then,
# we can use the DataFrame's index to repeat the operations on the BOLD data.
meta = meta[~meta['labels'].isin(['rest', 'scrambledpix'])]
meta = meta.sort_values('labels')
bold = nib.Nifti1Image(bold.get_fdata()[..., meta.index],
                       bold.affine, bold.header)

## Create model RDM.
# We're going to hunt for areas in the brain where the signal differentiates
# nicely between the various object categories.  We encode this objective in
# our "model" RDM: a RDM where stimuli belonging to the same object category
# have a dissimilarity of 0 and stimuli belonging to different categories have
# a dissimilarity of 1.
print('Computing model RDM...')
rdm_model = distance.pdist(meta[['labels']], lambda a, b: a != b)
viz.plot_rdm(rdm_model, meta.labels, title='Model RDM')

## Perform RSA analysis in a searchlight fashion.

# This is a mask that the authors provide. It is a GLM contrast based
# localizer map that extracts an ROI in the "ventral temporal" region.
roi_mask = nib.load(data_path / 'mask4_vt.nii.gz')

# Create searchlight patches around each voxel in the ROI
patches = searchlight.searchlight(bold, radius=2, roi_mask=roi_mask)

# Create an RDM for each searchlight patch and RSA against the model RDM
rsa_result = np.zeros(bold.shape[:3])  # result has no time dimension
for patch, seed_point in patches:
    rdm_patch = distance.pdist(patch.T, metric='correlation')
    rsa_result[seed_point], _ = spearmanr(rdm_model, rdm_patch)

# Packing the results in a Nifti1Image makes for easy saving and plotting
rsa_result = nib.Nifti1Image(rsa_result, bold.affine, bold.header)
nib.save(rsa_result, result_fname)
print(f'Saved result to: {result_fname}')

## Plot the RSA results.
# This uses one of NiLearn's plotting routines.
plotting.plot_glass_brain(rsa_result)
