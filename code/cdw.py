#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Functions for pipeline steps
Run with the interactive script

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-15
@notes:   Reorganised structure, spherical searchlight 
"""

from scipy import signal, stats
from scipy.spatial.distance import pdist, squareform, cdist
import numpy as np
import nibabel as nib
from itertools import compress

def load_preprocess(boldpath, labels):
    """
    Minimal preprocessing of BOLD-data
    
    Given a path to a 4D BOLD-data, loads it, then detrends and z-scores it
    run-wise ("chunks" in labels).

    Parameters
    ----------
    boldpath : str
        Path to original BOLD data.
    labels : DataFrame
        Labels for MRI frames.

    Returns
    -------
    bold_prep : Nifti1Image
        Preprocessed data.
    """
    
    print('Getting data...')
    bold = nib.load(boldpath)
    
    print('Copying data...')
    prep = bold.get_fdata().copy()  # memory hog?
    
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
            raise RuntimeWarning()
            print('Unexpected nans! Aborting.')
            return None
        
        prep[:,:,:,inds] = this_prep
    
    bold_prep = nib.Nifti1Image(prep, bold.affine, bold.header)
    print('Done.')
    return bold_prep

def reorder_data(bold_orig, labels, select_labels):
    """
    Reorders BOLD data accoring to selected conditions

    Parameters
    ----------
    bold_orig : Nifti1Image
        Original 4D BOLD data.
    labels : DataFrame
        Condition label of each MRI frame.
    select_labels : str array
        Labels of conditions selected for analysis.

    Returns
    -------
    conds : dict
        Dictionary that gives condition labels and their concomitant MRI
        frame indices.
    bold_conds : Nifti1Image
        Reordered 4D BOLD data.

    """
    
    # Get the inds of the MRI frames that pertain to each label, i.e. condition
    conds = {}
    for lab in select_labels:
        conds[lab] = labels.query('labels == @lab').index
    
    # Reorder data
    print('Reordering data and dropping unnecessary MRI frames...')
    bold_conds = np.concatenate(list(time2conds(bold_orig, conds)), axis=-1)
    print('Done.')
    
    return (conds, bold_conds)


def create_modelRDM(conds):
    # Makes the model RDM, given conditions
    
    # Get framecounts
    lens = [len(conds[k]) for k in conds.keys()]
    start_inds = np.cumsum(lens)
    start_inds = np.insert(start_inds,0,0)
    
    # Fill matrix according to framecounts
    rdm_model = np.ones((sum(lens),sum(lens)))
    for i in range(len(conds)):
        start = start_inds[i]
        stop = start_inds[i+1]
        rdm_model[start:stop, start:stop] = 0 
    
    return rdm_model


def calculate_maskRSA(bold, mask, rad, rdm_model):
    """
    Get RSA scores inside mask by searchlight
    
    Get a brain of RSA scores, calculated with a given radius of searchlight
    for voxels inside a given mask, and compared to model RDM.

    Parameters
    ----------
    bold_orig : Nifti1Image
        The original 4D BOLD data in chronological (time) order.
    mask : Nifti1Image
        A 3D mask to restrict the analysis with.
    rad : int
        Radius of searchlight (voxels). This currently defines a square, not
        a sphere -- subject to revision at a later point.
    rdm_model : ndarray
        The model RDM to compare the searchlight RDM to.

    Returns
    -------
    rsa_brain : ndarray
        RSA-scores in 3D brain space.
        
    """
    print('Calculating RSA...')
    rsa_brain = np.zeros(mask.shape)
    
    # Get (x,y,z) inds of all voxels inside mask
    inds = np.where(mask.get_fdata() == 1)
    print(f'Total number of voxels: {len(inds[0])}')
    
    # Get searchlight kernel (same for every voxel)
    kernel = make_searchlight(rad)
    
    # For each voxel in mask:
    i = 0
    for ind in zip(inds[0], inds[1], inds[2]):
        
        if i%100 == 0:
            print(f'{i} voxels done...')
        
        # Calc RDM in searchlight
        rdm_bold = calculate_boldRDM(bold, ind, kernel)
        
        # Calc RSA with model and save it
        (rho, p) = stats.spearmanr(rdm_bold, rdm_model, axis=None)
        rsa_brain[ind] = rho
        
        i += 1
    
    # Return RSA brain
    print('Done.')
    return rsa_brain

# =============================================================================
#                        INTERNAL HELPER FUNCTIONS
# =============================================================================
    

def calculate_boldRDM(bold, ind, kernel):
    # Calculates the data RDM in the given searchlight around voxel index ind
    
    # Get the searchlight voxels for this ind
    voxel_inds = [(ind[0]+k[0], ind[1]+k[1],ind[2]+k[2]) for k in kernel]
    voxels = np.vstack([bold[v[0],v[1],v[2],:] for v in voxel_inds]).T
    
    # Calculate dissimilarity
    rdm_bold = squareform(pdist(voxels, metric='correlation'))
    
    return rdm_bold


def make_searchlight(rad):
    # Makes a relative searchlight kernel (origo=(0,0,0)) with radius rad
    
    # Define a square, then filter out the corners (where dist > rad)
    rad_square = [(n[0]-rad,n[1]-rad,n[2]-rad) for n in np.ndindex(2*rad+1,2*rad+1,2*rad+1)]
    distances = cdist(rad_square, [(0,0,0)])
    kernel = list(compress(rad_square, distances <= rad))
    
    return kernel

def time2conds(bold, conds):
    # reorganise bold to conds
    for k in conds.keys():
        yield bold.get_fdata()[:,:,:,conds[k]]

