#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Main pipeline script

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-28
@notes:   Modified base logic after feedback
"""

import os
import pandas as pd
import numpy as np
import cdw
import nibabel as nib

datadir = '/Users/jenska/code/python/_misc/cdw2021/DATA'
subjs = ['subj1']


def run_group_rsa(subjs):
    pass
    # get rsa brains
    #rsa_brain = get_rsa_brain(subj)
    # calc grand mean
    #return rsa_grand_mean

def get_rsa_brain(subj,radius=2,force_prep=False,force_process=True):
    
    # Check whether we need to run the pipeline at all:
    is_saved = os.path.isfile(os.path.join(datadir,subj,'rsa_brain.nii'))
    if is_saved and not force_process:
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
        print('Using preprocessed data.')
        bold_prep = nib.load(os.path.join(datadir,subj,'bold_prep.nii'))
    else:
        print('Getting original data...')
        bold = nib.load(os.path.join(datadir,subj,'bold.nii.gz'))
        bold_prep = cdw.preprocess(bold, labels)
        nib.save(bold_prep,os.path.join(datadir,subj,'bold_prep.nii'))
        print('Preprocessed data saved.')
    
    # Drop "bad" labels
    bad_labels = ['rest','scrambledpix']
    (bold_prep, labels) = cdw.drop_by_labels(bold_prep,labels,bad_labels)
    
    # Reorder data and labels
    (bold_prep, labels) = cdw.reorder_by_labels(bold_prep,labels)
    
    # Make model rdm
    rdm_model = cdw.create_modelRDM(labels)
    
    # Run analysis
    print('Calculating RSA...')
    rad = radius
    rsa_brain = np.zeros(roi_mask.shape)
    
    i = 0
    for (center_ind, patch_data) in cdw.get_patch_data(bold_prep, roi_mask, rad):
        
        rdm_bold = cdw.calc_data_rdm(patch_data)
        rsa_brain[center_ind] = cdw.calc_rsa(rdm_bold, rdm_model)
        
        if i%100 == 0:
            print(f'{i} voxels done...')
        i += 1
    
    print('Done.')
    
    # Wrap up as nifti
    rsa_brain_nii = nib.Nifti1Image(rsa_brain, bold_prep.affine, bold_prep.header)
    
    # Save
    nib.save(rsa_brain_nii,os.path.join(datadir,subj,'rsa_brain.nii'))
    print('Saved RSA brain.')

    return rsa_brain_nii


