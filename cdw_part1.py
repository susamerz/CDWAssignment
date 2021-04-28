import numpy as np
import pandas as pd
import matplotlib as mp
import scipy as sc
from scipy import signal
import nibabel as nib
import nilearn as nil
from scipy.spatial import distance
from scipy.stats import spearmanr

def preprocess(chunk):
    # Detrends and z-scores one chunk of BOLD MRI data
    
    for x_dim in range(chunk.shape[0]):
        for y_dim in range(chunk.shape[1]):
            for z_dim in range(chunk.shape[2]):
                # now we have one voxel timeseries
                
                voxel_ts = chunk[x_dim, y_dim, z_dim, :]
                chunk[x_dim, y_dim, z_dim, :] = sc.stats.zscore(sc.signal.detrend(voxel_ts), axis=-1)
    
    return chunk            
    
def get_one_RSA(subject_no, path, searchlight_radius):
    
    bold = nib.load('{}subj{}/bold.nii.gz'.format(path, subject_no))    
    mask = nib.load('{}subj{}/mask4_vt.nii.gz'.format(path, subject_no))  
    labels_path = '{}subj{}/labels.txt'.format(path, subject_no)      
    labels = pd.read_csv(labels_path, sep=' ')  
    
    bold_data = bold.get_fdata()
    
    # make 5-dimensional numpy array for chunk data
    chunks = []
    
    group_indices = labels.groupby('chunks').indices   
       
    for _, indices in group_indices.items():
        bold_chunk = bold_data[:, :, :, indices]
        #bold_chunk = preprocess(np.array(bold_chunk))
        chunks.append(bold_chunk)
        
    chunks = np.array(chunks)
    # shape of chunks is (12, 40, 64, 64, 121)
    bold_data = chunks.reshape(bold_data.shape)
    # shape (40, 64, 64, 1452)
    
    # remove unwanted labels
    index_names = labels[(labels['labels'] == 'rest') | (labels['labels'] == 'scrambledpix')].index
    labels.drop(index_names, inplace = True)
    group_indices = labels.groupby('chunks').indices # new
    
    # drop MR images corresponding to the dropped labels    
    bold_data = bold_data[:, :, :, labels.index]
    # shape (40, 64, 64, 756)
    
    # make new chunks
    chunks = []
    for _, indices in group_indices.items():
        bold_chunk = bold_data[:, :, :, indices]
        chunks.append(bold_chunk)
        
    chunks = np.array(chunks)
    
    # ------------- Compute model RDM ----------    
    # square matrix with diagonal of zeros and ones elsewhere    
    n_images = chunks.shape[4]
    mRDM = np.zeros((n_images, n_images))
    
    for i in range(mRDM.shape[0]):
        for j in range(mRDM.shape[1]):
            if labels['labels'].values[i] == labels['labels'].values[j]:
                mRDM[i, j] = 0
            else:
                mRDM[i, j] = 1
    
    # flatten model RDM into vector
    mRDMvec = mRDM.flatten() # length 3969
     
    # -------------Make searchlights around each voxel------
    # --> loop through voxels in ROI and make searchlight centering on each
    
    mask_data = mask.get_fdata()
    RSA = np.zeros(((bold_data.shape[0], bold_data.shape[1], bold_data.shape[2])))
    
    voxel_grid = np.array(list(np.ndindex(bold_data.shape[:3])))
    searchlight_grid = distance.cdist(np.array(mask_data.nonzero()).T,voxel_grid) <= searchlight_radius
    # shape (577, 163840)
    
    bold_data_flat = bold_data.reshape(-1, bold_data.shape[-1])
    
    for voxel in list(range(searchlight_grid.shape[0])):
            
        images = bold_data_flat[searchlight_grid[voxel].nonzero()].T # size (756, 33)
        
        RDM = distance.squareform(distance.pdist(images, metric='correlation'))
        RDMvec = RDM.flatten() # length 571536
        
        # compute RSA
        RSA[x_dim,y_dim,z_dim] = spearmanr(mRDMvec, RDMvec)[0]
        # --> ERROR: vector lengths don't match
        
        
    return RSA
    
def main():   
    
    #group level analysis
    no_of_subjects = 6
    searchlight_radius = 2
    
    allRSA = np.zeros(no_of_subjects)
    
    path = "../CDWAssignment_data/"
    
    for subject in range(1,no_of_subjects+1):
        allRSA[subject] = get_one_RSA(subject, path, searchlight_radius)
    
    # compute mean RSA across all subjects
    
    
    # ------------------Make image of RSA values in ROI-----------
    RSA_plotting = nib.Nifti1Image(mean_RSA, bold.affine)
    
    nil.plotting.plot_glass_brain(RSA_plotting)
    
main()
