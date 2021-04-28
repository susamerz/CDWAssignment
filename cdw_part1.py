from re import search
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import scipy as sc
from scipy import signal
import nibabel as nib
from nilearn import plotting
from scipy.spatial import distance
from scipy.stats import spearmanr
    
    
def get_one_RSA(subject_no, path, searchlight_radius):
    
    bold = nib.load(f'{path}/subj{subject_no}/bold.nii.gz')    
    mask = nib.load(f'{path}/subj{subject_no}/mask4_vt.nii.gz')  
    
    labels_path = f'{path}/subj{subject_no}/labels.txt'
    
    labels = pd.read_csv(labels_path, sep=' ')  
    
    bold_data = bold.get_fdata()
    
    chunks = []
    
    group_indices = labels.groupby('chunks').indices   
       
    for _, indices in group_indices.items():
        bold_chunk = np.array(bold_data[:, :, :, indices])
        # preprocess
        bold_chunk = sc.stats.zscore(sc.signal.detrend(bold_chunk, axis=-1), axis=-1)
        chunks.append(bold_chunk)
        
    chunks = np.array(chunks)
    bold_data = chunks.reshape(bold_data.shape)
    
    # remove unwanted labels
    index_names = labels[(labels['labels'] == 'rest') | (labels['labels'] == 'scrambledpix')].index
    labels.drop(index_names, inplace = True)
    
    # drop MR images corresponding to the dropped labels    
    bold_data = bold_data[:, :, :, labels.index]
        
    # ------------- Compute model RDM ----------    
    # square matrix with diagonal of zeros and ones elsewhere    
    n_images = bold_data.shape[3]
    mRDM = np.zeros((n_images, n_images))
    
    for i in range(mRDM.shape[0]):
        for j in range(mRDM.shape[1]):
            if labels['labels'].values[i] == labels['labels'].values[j]:
                mRDM[i, j] = 0
            else:
                mRDM[i, j] = 1
    
    mRDMvec = mRDM.flatten()
     
    # -------------Make searchlights around each voxel------
    # --> loop through voxels in ROI and make searchlight centering on each
    
    mask_data = mask.get_fdata()
    rsa_values = np.zeros((mask_data == 1).sum())
    
    RSA = np.zeros(((bold_data.shape[0], bold_data.shape[1], bold_data.shape[2])))
    
    voxel_grid = np.array(list(np.ndindex(bold_data.shape[:3])))
    searchlight_grid = distance.cdist(np.array(mask_data.nonzero()).T,voxel_grid) <= searchlight_radius
    
    bold_data_flat = bold_data.reshape(-1, bold_data.shape[-1])
    
    for voxel in list(range(searchlight_grid.shape[0])):
            
        images = bold_data_flat[searchlight_grid[voxel].nonzero()].T
        
        RDM = distance.squareform(distance.pdist(images, metric='correlation'))
        RDMvec = RDM.flatten()
        
        rsa_values[voxel] = spearmanr(mRDMvec, RDMvec)[0]
    
    RSA[mask_data == 1] = rsa_values   
        
    return RSA
    
def main():   
    
    # group level analysis: input wanted subject ids
    subject_ids = [1]
    searchlight_radius = 2
    path = "../CDWAssignment_data"
    
    bold = nib.load(f'{path}/subj{subject_ids[0]}/bold.nii.gz')
    bold_data = bold.get_fdata()
    
    allRSA = np.zeros((((len(subject_ids),bold_data.shape[0], bold_data.shape[1], bold_data.shape[2]))))
       
    for index in range(len(subject_ids)):
        allRSA[index,:,:,:] = get_one_RSA(subject_ids[index], path, searchlight_radius)
    
    # compute mean RSA across all subjects
    mean_RSA = allRSA.mean(axis=0)
    
    # ------------------Make image of RSA values in ROI-----------
    RSA_plotting = nib.Nifti1Image(mean_RSA, bold.affine)
    
    plotting.plot_glass_brain(RSA_plotting)
    
main()
