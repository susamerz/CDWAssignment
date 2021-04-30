#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Main pipeline script

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-28
@notes:   Modified logic after feedback, added assignment 2
"""

import os
import pandas as pd
import numpy as np
import cdw
import nibabel as nib
import matplotlib.pyplot as plt

datadir = '/Users/jenska/code/python/_misc/cdw2021/DATA'

def run_group_rsa(subjs, **kwargs):
    """
    Run group RSA analysis

    Parameters
    ----------
    subjs : list of str
        Names of directories containing data for each individual subject.
    **kwargs : keyword arguments
        See get_rsa_brain().

    Returns
    -------
    rsa_mean_nii : Nifti1Image
        Brain image containing mean RSA values across subjects.

    """
    
    list_of_brains = []
    for s in subjs:
        print(f'\n-------**  Processing {s}  **-------')
        list_of_brains.append(get_rsa_brain(s, **kwargs))
    
    print('\nCalculating grand mean...')
    rsa_data = np.stack([brain.get_fdata() for brain in list_of_brains])
    rsa_mean = rsa_data.mean(axis=0)
    rsa_mean_nii = nib.Nifti1Image(rsa_mean, list_of_brains[0].affine)
    print('Done.')
    
    return rsa_mean_nii


def get_rsa_brain(subj,radius=2,force_prep=False,force_rsa_calc=False):
    """
    Calculate RSA for one subject

    Parameters
    ----------
    subj : str
        Name of directory containing data for subject.
    radius : int, optional
        Radius of searchlight, voxels. The default is 2.
    force_prep : bool, optional
        Whether to force preprocessing, even if file already exists. The
        default is False.
    force_calc_rsa : bool, optional
        Whether to force RSA calculation, even if file already exists. The
        default is False.

    Returns
    -------
    rsa_brain_nii : Nifti1Image
        RSA scores in brain space.

    """
    
    #  ----------- Do we need to run the pipeline at all? ----------
    
    is_saved = os.path.isfile(os.path.join(datadir,subj,'rsa_brain.nii'))
    if is_saved and not force_rsa_calc:
        print('Returning previously calculated RSA brain.')
        rsa_brain_nii = nib.load(os.path.join(datadir,subj,'rsa_brain.nii'))
        return rsa_brain_nii
    
    
    # --------------- Decided to run the pipeline. -----------------
    
    print('Running the pipeline.')
    labels = pd.read_csv(os.path.join(datadir,subj,'labels.txt'), sep=' ')
    roi_mask = nib.load(os.path.join(datadir,subj,'mask4_vt.nii.gz'))
    
    # Preprocess if needed or requested:
    is_prep = os.path.isfile(os.path.join(datadir,subj,'bold_prep.nii'))
    if is_prep and not force_prep:
        print('Loading preprocessed data.')
        bold_prep = nib.load(os.path.join(datadir,subj,'bold_prep.nii'))
    else:
        print('Getting original data...')
        bold = nib.load(os.path.join(datadir,subj,'bold.nii.gz'))
        bold_prep = cdw.preprocess(bold, labels)
        print('Saving data...')
        nib.save(bold_prep,os.path.join(datadir,subj,'bold_prep.nii'))
        print('Done.')
    
    # Drop "bad" labels
    bad_labels = ['rest','scrambledpix']
    (bold_prep, labels) = cdw.drop_by_labels(bold_prep,labels,bad_labels)
    
    # Reorder data and labels
    (bold_prep, labels) = cdw.reorder_by_labels(bold_prep,labels)
    
    # Make model rdm
    rdm_model = cdw.create_model_rdm(labels)
    
    # Run analysis
    print('Calculating RSA...')
    rad = radius
    rsa_brain = np.zeros(roi_mask.shape)
    
    i = 0
    for (center_ind, patch_data) in cdw.get_patch_data(bold_prep, roi_mask, rad):
        
        # Calculate RSA for patch, save to center voxel
        rdm_bold = cdw.calc_data_rdm(patch_data)
        rsa_brain[center_ind] = cdw.calc_rsa(rdm_bold, rdm_model)
        
        if i%100 == 0:
            print(f'{i} voxels done...')
        i += 1
    
    print('All done.')
    
    # Wrap up as nifti
    rsa_brain_nii = nib.Nifti1Image(rsa_brain, bold_prep.affine, bold_prep.header)
    
    # Save
    nib.save(rsa_brain_nii,os.path.join(datadir,subj,'rsa_brain.nii'))
    print('Saved RSA brain.')

    return rsa_brain_nii


if __name__ == "__main__":
    
    # Process all subjects in datadir
    subjs = [s for s in os.listdir(datadir) if 'subj' in s]
    print(f'Found {len(subjs)} subjects.')
    rsa_grand_mean = run_group_rsa(subjs)
    
    # Save grand mean RSA brain
    nib.save(rsa_grand_mean,os.path.join(datadir,'rsa_grand_mean.nii'))
