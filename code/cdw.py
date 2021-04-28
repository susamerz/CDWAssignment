#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Functions for pipeline steps

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-28
@notes:   Redo after feedback, some docstrings missing
"""

from scipy import signal, stats
from scipy.spatial.distance import pdist, squareform, cdist
import numpy as np
import pandas as pd
import nibabel as nib
from itertools import compress


def preprocess(bold, labels):
    """
    Minimal preprocessing of BOLD data
    
    Given a 4D BOLD-data detrends and z-scores it
    run-wise ("chunks" in labels).

    Parameters
    ----------
    bold : Nifti1Image
        Original BOLD data.
    labels : DataFrame
        Labels for MRI frames.

    Returns
    -------
    bold_prep : Nifti1Image
        Preprocessed data.
    """
    
    print('Copying data...')
    prep = bold.get_fdata()
    
    print('Done. Begin preprocessing...')
    for c in labels.chunks.unique():
        print('Processing chunk ' + str(c))
        inds = labels.query('chunks == @c').index
        this_prep = prep[:,:,:,inds]
        this_prep = signal.detrend(this_prep)
        this_prep = stats.zscore(this_prep, axis=-1)
        
        # scipy z-score does not watch out for zero-division, so
        # we have to correct those ourselves. Replacing nans with
        # zeros makes sense as long as the input is all zeros, too.
        if prep[:,:,:,inds][np.isnan(this_prep)].sum() == 0:
            this_prep[np.isnan(this_prep)] = 0
        else:
            raise Exception('Unexpected nans! Aborting.')
        
        prep[:,:,:,inds] = this_prep
    
    bold_prep = nib.Nifti1Image(prep, bold.affine, bold.header)
        
    print('Done.')
    return bold_prep

def drop_by_labels(bold, labels, bad_labels):
    """
    Drop unwanted labels and fMRI frames
    
    Takes a 4D BOLD image and drops frames that correspond to unwanted
    labels, and also drops those labels from the labels DataFrame.

    Parameters
    ----------
    bold : Nifti1Image
        Full 4D BOLD image.
    labels : DataFrame
        Full list of frame labels.
    bad_labels : list of str
        Unwanted labels.

    Returns
    -------
    bold_subset : Nifti1Image
        Selected BOLD frames.
    labels_subset : DataFrame
        Selected frame labels.

    """
    
    good_inds = labels.query('labels not in @bad_labels').index
    labels_subset = labels.loc[good_inds]
    
    print('Dropping unwanted frames...')
    frames_subset = bold.get_fdata()[:,:,:,good_inds]
    bold_subset = nib.Nifti1Image(frames_subset, bold.affine, bold.header)
    
    print('Done.')
    return (bold_subset, labels_subset)
    

def reorder_by_labels(bold, labels):
    """
    Reorder labels and frames of 4D BOLD image
    
    Sorts labels (of frames) alphabetically and then reorders BOLD frames
    to match that order.

    Parameters
    ----------
    bold : Nifti1Image
        Original 4D BOLD image.
    labels : DataFrame
        Original frame labels.

    Returns
    -------
    bold_sorted : Nifti1Image
        Sorted 4D BOLD image..
    labels_sorted : DataFrame
        Sorted frame labels.

    """
    
    labels['fmri_i'] = range(len(labels))
    labels_sorted = labels.sort_values(by=['labels','chunks'])
    labels_sorted.reset_index(inplace=True)
    
    print('Reordering data...')
    frames_sorted = bold.get_fdata()[:,:,:,labels_sorted['fmri_i']]
    bold_sorted = nib.Nifti1Image(frames_sorted, bold.affine, bold.header)
    
    print('Done.')
    return (bold_sorted, labels_sorted)


def create_modelRDM(labels):
    # Makes the model RDM, given labels
    
    # To get an "identity matrix" over labels we first expand labels to dummies
    # (one column per label with values=[0,1]) and then get the dot product of
    # that and its transpose -- result is 1 when the labels of the frame match,
    # and 0 when they don't. To get RDM, switch those.
    dummies = pd.get_dummies(labels.labels).to_numpy()
    rdm_model = np.dot(dummies, dummies.T)
    rdm_model = abs(rdm_model-1)
    
    return rdm_model


def get_patch_data(bold, mask, rad):
    
    # Get (x,y,z) inds of all voxels inside mask
    inds = np.where(mask.get_fdata() == 1)
    print(f'Number of voxels in mask:: {len(inds[0])}')
    
    # Create searchlight kernel
    kernel = _make_searchlight(rad)
    print(f'Number of voxels in searchlight: {len(kernel)}')
    
    # For each voxel, get and return patch data
    for center_ind in zip(inds[0], inds[1], inds[2]):
        
        # Get inds for this patch
        patch_inds = []
        for (kx,ky,kz) in kernel:
            patch_inds.append( (center_ind[0]+kx,
                                center_ind[1]+ky,
                                center_ind[2]+kz) )
        
        # Get the bold data for the patch
        patch_data = np.vstack([bold.get_fdata()[x,y,z,:] for (x,y,z) in patch_inds]).T
        
        yield (center_ind, patch_data)


def calc_data_rdm(patch_data):
    
    # Calculate dissimilarity of patterns at each frame
    rdm = squareform(pdist(patch_data, metric='correlation'))
    
    return rdm


def calc_rsa(rdm_bold, rdm_model):
    
    # Calculate RSA score for the two RDMs 
    (rsa_score, _) = stats.spearmanr(rdm_bold, rdm_model, axis=None)
    
    return rsa_score

# =============================================================================
#                        INTERNAL HELPER FUNCTIONS
# =============================================================================
    

def _make_searchlight(rad):
    # Makes a relative searchlight kernel (origo=(0,0,0)) with radius rad
    
    # Define a square, then filter out the corners (where dist > rad)
    diam = 2*rad+1
    rad_square = []
    for (x,y,z) in np.ndindex(diam,diam,diam):
        rad_square.append( (x-rad,y-rad,z-rad) ) # put origo in center of square
    
    distances = cdist(rad_square, [(0,0,0)])
    kernel = list(compress(rad_square, distances < rad))
    
    return kernel


