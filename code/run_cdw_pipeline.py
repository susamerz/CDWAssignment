#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Runner script

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-15
@notes:   Reorganised function structure
"""
import os
import pandas as pd
import cdw
import nibabel as nib
from nilearn import plotting

datadir = '/Users/jenska/code/python/_misc/cdw2021/DATA'
subj = 'subj1'

boldfile = 'bold.nii.gz'
labfile = 'labels.txt'
maskfile = 'mask4_vt.nii.gz'

#%% Load labels and mask
labels = pd.read_csv(os.path.join(datadir,subj,labfile), sep=' ')
mask = nib.load(os.path.join(datadir,subj,maskfile))

#%% Load & preprocess BOLD data
boldpath = os.path.join(datadir,subj,boldfile)
bold_prep = cdw.load_preprocess(boldpath, labels)

#%% Save prepro
nib.save(bold_prep,os.path.join(datadir,subj,'bold_prep.nii'))

#%% Load prepro
bold_prep = nib.load(os.path.join(datadir,subj,'bold_prep.nii'))

#%% Analysis conditions

# Subset of labels (conditions) to include in the model
select_labels = ['bottle','cat','chair','face','house','scissors','shoe']

# Reorder data accoring to conds
(conds, bold_conds) = cdw.reorder_data(bold_prep, labels, select_labels)

# Get model RDM
rdm_model = cdw.create_modelRDM(conds)

#%% Run analysis

rad = 2 # radius of searchlight, voxels
rsa_brain = cdw.calculate_maskRSA(bold_conds, mask, rad, rdm_model)

# Wrap up as nifti
rsa_brain_nii = nib.Nifti1Image(rsa_brain, bold_prep.affine, bold_prep.header)

#%% Plot
plotting.plot_glass_brain(rsa_brain_nii)

#%% Save for later
nib.save(rsa_brain_nii,os.path.join(datadir,subj,'rsa_brain2.nii'))
