#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Runner script

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-14
@notes:   
"""
import os
import pandas as pd
#import numpy as np
import cdw
import nibabel as nib
from nilearn import plotting

datadir = '/Users/jenska/code/python/_misc/cdw2021/DATA'
subj = 'subj1'

boldfile = 'bold.nii.gz'
labfile = 'labels.txt'
maskfile = 'mask4_vt.nii.gz'

labels = pd.read_csv(os.path.join(datadir,subj,labfile), sep=' ')

#%% Load & preprocess BOLD data
boldpath = os.path.join(datadir,subj,boldfile)
bold_prep = cdw.load_preprocess(boldpath, labels)

#%% Save prepro
nib.save(bold_prep,os.path.join(datadir,subj,'bold_prep.nii'))

#%% Load prepro
bold_prep = nib.load(os.path.join(datadir,subj,'bold_prep.nii'))

#%% Prepare for RSA

# Subset of labels to include in the model
select_labels = ['bottle','cat','chair','face','house','scissors','shoe']

# Get the inds of the MRI frames that pertain to each label, i.e. condition
conds = {}
for lab in select_labels:
    conds[lab] = labels.query('labels == @lab').index

# Load mask
maskpath = os.path.join(datadir,subj,maskfile)
mask = nib.load(maskpath)

#%% Run RSA
rad = 1 # radius of searchlight, voxels
rsa_brain = cdw.getRSA(bold_prep, mask, rad, conds)

#%% Plot
plotting.plot_glass_brain(rsa_brain)

