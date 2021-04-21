#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 14:50:12 2021

@author: jenska
"""
import os
from nilearn import plotting
import nibabel as nib
import pandas as pd
from scipy import signal, stats
import numpy as np
import matplotlib.pyplot as plt
import cdw

datadir = '/Users/jenska/code/python/_misc/cdw2021/DATA'
subj = 'subj1'

boldfile = 'bold.nii.gz'
labfile = 'labels.txt'
maskfile = 'mask4_vt.nii.gz'

#%% Get data
bold = nib.load(os.path.join(datadir,subj,boldfile))
labels = pd.read_csv(os.path.join(datadir,subj,labfile), sep=' ')

#%% Run pipeline
bold_prep = preprocess(bold, labels)


#%% plotchecks
#inds = labels.query('chunks == 0').index
plotdata = bold_prep.slicer[:,:,:,60]
plotting.plot_glass_brain(plotdata)

#%% Preprocessing
def preprocess(bold, labels):
    
    chunks = labels.chunks.unique()
    prep = bold.get_fdata().copy()
    
    for c in chunks:
        inds = labels.query('chunks == @c').index
        this_prep = prep[:,:,:,inds]
        this_prep = signal.detrend(this_prep)
        this_prep = stats.zscore(this_prep, axis=-1)
        prep[:,:,:,inds] = this_prep
    
    bold_prep = nib.Nifti1Image(prep, bold.affine, bold.header)
    return bold_prep

#%% Building BOLD RDM

# for each MRI frame make vector
# calc dissimilarity (1–pearson) between all time frames?? srsly?
# pretty sure not -- we just want the chunks is all
# we should also get rid of unmask voxels

# Select and order MRI frames based on labels

N = bold_prep.shape[1]
rdm = np.zeros(shape=(N,N))
for i in range(N):
    for j in range(N):
        (r,p) = stats.pearsonr(bold_prep.get_fdata()[:,i], 
                                  bold_prep.get_fdata()[:,j])
        rdm[i,j] = 1 - r

#(r,p) = stats.pearsonr(fr1,fr2)

#%% Building model RDM
maskpath = os.path.join(datadir,subj,maskfile)
mask = nib.load(maskpath)

# create new empty img (like mask)
rsa_brain = np.zeros(mask.shape)

# Find searchlight voxels (27)
inds = np.where(mask.get_fdata() == 1)
for (i,j,k) in zip(inds[0], inds[1], inds[2]):
    #print(f'({i}, {j}, {k})')

#%% define kernel
ind = (30, 26, 28)
rad = 2

voxels = bold_prep.get_fdata()[ ind[0]-rad: ind[0]+rad+1,
                             ind[1]-rad: ind[1]+rad+1,
                             ind[2]-rad: ind[2]+rad+1, :]

# compute the RSA

# first rdm for voxels

# then with model

# save into new data (at voxel ind)
rsa_brain[ind] = rsa


#%%
bold_conds = np.concatenate(list(cdw.time2conds(bold_prep, conds)), axis=-1)

#%%
ind = (30, 26, 28)
rad = 1
rdm = cdw.calculate_boldRDM(bold_conds, ind, rad)

#%%
plt.imshow(rdm)


#%%
# RSA

# Searchlight

# Plot