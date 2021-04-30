#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Functions for pipeline steps

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-28
@notes:   Redo after feedback
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
        print(f'Processing chunk {c}')
        inds = labels.query('chunks == @c').index
        this_prep = prep[:,:,:,inds]
        this_prep = signal.detrend(this_prep)
        this_prep = stats.zscore(this_prep, axis=-1)
        
        # scipy z-score does not watch out for zero-division, so
        # we have to correct those ourselves. Replacing nans with
        # zeros makes sense as long as the input is all zeros, too.
        if np.all(prep[...,inds][np.isnan(this_prep)] == 0):
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
    frames_subset = bold.get_fdata()[...,good_inds]
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
    
    labels['orig_bold_ind'] = range(len(labels))
    labels_sorted = labels.sort_values(by=['labels','chunks'],ignore_index=True)
    
    print('Reordering data...')
    frames_sorted = bold.get_fdata()[:,:,:,labels_sorted['orig_bold_ind']]
    bold_sorted = nib.Nifti1Image(frames_sorted, bold.affine, bold.header)
    
    print('Done.')
    return (bold_sorted, labels_sorted)


def create_model_rdm(labels):
    """
    Create RDM from labels
    
    Creates a theoretical representational dissimilarity matrix that
    discriminates between all the given categories: dissimilarity within
    label is 0, between labels 1.

    Parameters
    ----------
    labels : DataFrame
        Labels of frames (sorted).

    Returns
    -------
    rdm_model : ndarray
        Theoretical RDM.

    """
    
    def dissimilarity(label1, label2):
        return label1 != label2

    rdm_model = squareform(pdist(labels[['labels']], metric=dissimilarity))
    
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
        patch_inds = np.add(center_ind, kernel)
        
        # Get the bold data for the patch
        patch_data = bold.get_fdata()[tuple(patch_inds.T)].T
        
        yield (center_ind, patch_data)


def calc_data_rdm(patch_data):
    """
    Calculate RDM
    
    Returns representational dissimilarity matrix for a patch of data.

    Parameters
    ----------
    patch_data : ndarray
        BOLD data (frames x voxels).

    Returns
    -------
    rdm : ndarray
        Representational dissimilarity matrix (frames x frames).

    """
    
    rdm = squareform(pdist(patch_data, metric='correlation'))
    
    return rdm


def calc_rsa(rdm_bold, rdm_model):
    """
    Calculate RSA
    
    Calculates representational similarity score between given RDMs.

    Parameters
    ----------
    rdm_bold : ndarray
        RDM from BOLD data.
    rdm_model : ndarray
        RDM defined by model.

    Returns
    -------
    rsa_score : float
        Correlation between the matrices.

    """
    
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


