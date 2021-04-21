#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Functions for pipeline steps
Run with the interactive script

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-14
@notes:   
"""

from scipy import signal, stats
import numpy as np
import nibabel as nib

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


def getRSA(bold_orig, mask, rad, conds):
    """
    Get RSA scores by searchlight
    
    Get a brain of RSA scores, calculated with a given radius of searchlight
    for voxels inside a given mask. Conds should give indices of MRI frames for
    each condition.

    Parameters
    ----------
    bold_orig : Nifti1Image
        The original 4D BOLD data in chronological (time) order.
    mask : Nifti1Image
        A 3D mask to restrict the analysis with.
    rad : int
        Radius of searchlight (voxels). This currently defines a square, not
        a sphere -- subject to revision at a later point.
    conds : dict
        Dictionary with condition names as keys and arrays of MRI frame
        indices as values.

    Returns
    -------
    rsa_brain : numpy array
        RSA-scores in brain space.
    """
    
    rsa_brain = np.zeros(mask.shape)
    
    # Reorder bold data into "condition order"  & drop extra frames
    print('Reordering data and dropping unnecessary MRI frames...')
    bold_conds = np.concatenate(list(time2conds(bold_orig, conds)), axis=-1)
    print('Done. Calculating RSA...')
    
    rdm_model = create_modelRDM(conds)

    inds = np.where(mask.get_fdata() == 1)
    print(f'Total number of voxels: {len(inds[0])}')
    
    # For each voxel in mask:
    i = 0
    for ind in zip(inds[0], inds[1], inds[2]):
        
        if i%100 == 0:
            print(f'{i} voxels done...')
        
        # Calc rdm in searchlight
        rdm_bold = calculate_boldRDM(bold_conds, ind, rad)
        
        # Calc rsa and save it
        rsa_brain[ind] = calculate_RSA(rdm_bold, rdm_model)
        
        i += 1
        
    # Wrap up as nifti
    rsa_brain_nii = nib.Nifti1Image(rsa_brain, bold_orig.affine, bold_orig.header)
    
    # return rsa brain
    print('Done.')
    return rsa_brain_nii

# =============================================================================
#                        INTERNAL HELPER FUNCTIONS
# =============================================================================

def create_modelRDM(conds):
    # makes the model rdm, given conds
    
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

def calculate_boldRDM(bold, ind, rad):
    # calc the rdm in given searchlight beam
    
    # TODO: fix the radius thing
    # Get voxels inside radius (square for now)
    voxels = bold[ind[0]-rad: ind[0]+rad+1,
                   ind[1]-rad: ind[1]+rad+1,
                   ind[2]-rad: ind[2]+rad+1, :]
    
    # Flatten in all but last dimension (MRI frames)
    n_frames = voxels.shape[-1]
    voxels = np.vstack([ voxels[:,:,:,i].flatten() for i in range(n_frames) ])
    
    # Matrix approach to calculating the r (scipy pair-wise is SLOW)
    # NOTE: this works only as long as there are no nans!
    if not np.isnan(voxels).any():
        rdm_bold = 1 - np_pearson_cor(voxels.T, voxels.T)
    else:
        raise RuntimeError
        print('Nans in voxels! Aborting.')
        return None
    
    return rdm_bold

def calculate_RSA(rdm_bold, rdm_model):
    # take the RDMs and calc their rsa
    (rho, p) = stats.spearmanr(rdm_bold, rdm_model, axis=None)
    return rho

def time2conds(bold, conds):
    # reorganise bold to conds
    for k in conds.keys():
        yield bold.get_fdata()[:,:,:,conds[k]]

def np_pearson_cor(x, y):
    # From https://cancerdatascience.org/blog/posts/pearson-correlation/
    
    xv = x - x.mean(axis=0)
    yv = y - y.mean(axis=0)
    xvss = (xv * xv).sum(axis=0)
    yvss = (yv * yv).sum(axis=0)
    result = np.matmul(xv.transpose(), yv) / np.sqrt(np.outer(xvss, yvss))
    
    # bound the values to -1 to 1 in the event of precision issues
    return np.maximum(np.minimum(result, 1.0), -1.0)