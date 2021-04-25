import numpy as np
import pandas as pd
import matplotlib as mp
import scipy as sc
from scipy import signal
import nibabel as nib
import nilearn as nil

def preprocess(chunks):
    i = 0
    for chunk in chunks:
        for x_dim in range(chunk.shape[0]):
            for y_dim in range(chunk.shape[1]):
                for z_dim in range(chunk.shape[2]):
                    # now we have one voxel timeseries
                    # remove linear trend and z-score the data
                    
                    voxel_ts = chunk[x_dim, y_dim, z_dim, :]
                    voxel_ts_detrend = sc.signal.detrend(voxel_ts, axis=-1)
                    voxel_ts_processed = sc.stats.zscore(voxel_ts_detrend, axis=-1)
                    
                    chunk[x_dim, y_dim, z_dim, :] = voxel_ts_processed;
                    
        chunks[i] = chunk
        i += 1
        
    return chunks            
    

    
def main():
    
    bold = nib.load('../CDWAssignment_data/subj1/bold.nii.gz')
    
    mask = nib.load('../CDWAssignment_data/subj1/mask4_vt.nii.gz')
    #voxels_in_roi = bold.get_fdata()[mask.get_fdata() == 1, :] # 577 voxels
           
    labels = pd.read_csv('../CDWAssignment_data/subj1/labels.txt', sep=' ')
    '''
    # make 5-dimensional numpy array for chunk data
    # size 40x64x64x[time_length_of_chunk]x11
    chunks = [];
    
    for i in range(12):
        labels_chunk = labels.query('chunks == %d' % (i))
        bold_chunk = bold.get_fdata()[:, :, :, labels_chunk.index]
        chunks.append(bold_chunk)
        
    chunks_np = np.array(chunks)
    
    # pre-process all chunks
    chunks_np_pp = preprocess(chunks_np)
    
    # ------------- Compute model RDM ----------
    # first, get labels of images
    
    # remove unwanted labels: rest and scrambledpix
    index_names = labels[(labels['labels'] == 'rest') | (labels['labels'] == 'scrambledpix')].index
    labels.drop(index_names, inplace = True)
    
    # get amount of leftover labels
    unique_labels = labels['labels'].unique()
    no_of_labels = len(unique_labels)
    
    # construct model RDM: square matrix with diagonal of zeros and ones elsewhere    
    n_images = chunks_np_pp.shape[3]
    mRDM = np.zeros((n_images, n_images))
    
    for i in range(mRDM.shape[0]):
        for j in range(mRDM.shape[1]):
            if labels['labels'].values[i] == labels['labels'].values[j]:
                mRDM[i, j] = 0
            else:
                mRDM[i, j] = 1
    
    # flatten model RDM into vector
    mRDMvec = mRDM.flatten()
        
    # -------------Make searchlights around each voxel------
    # --> loop through voxels in ROI and make searchlight centering on each
    '''
    bold_array = bold.get_fdata()
    mask_array = mask.get_fdata()
    voxel_grid = np.zeros(((bold_array.shape[0], bold_array.shape[1], bold_array.shape[2])))
    
    for i,j,k in np.ndindex(bold_array.shape[:3]):
        voxel_grid[i,j,k] = [[i,j,k]]
    
    RSA = np.zeros(((bold_array.shape[0], bold_array.shape[1], bold_array.shape[2])))
    
    radius = 2
    
    for x_dim,y_dim,z_dim in np.ndindex(bold_array.shape[:3]):
        # now we have one voxel timeseries 
        
        if mask_array[x_dim,y_dim,z_dim] == 1:
            print('Voxel in ROI: computing searchlight \n')
            print('WOOP WOOP \n')
            
            centerpoint = [[x_dim,y_dim,z_dim]]
            
            distances = sc.spatial.distance.cdist(centerpoint, voxel_grid, 'euclidean')   
            searchlight = bold_array[bold_array[distances <= radius]]

            '''
            # compute RDM and flatten into vector
            RDM = sc.spatial.distance.pdist(searchlight, 'correlation')
            RDM = sc.spatial.distance.squareform(RDM)
            RDMvec = flatten(RDM)
            
            # compute RSA
            RSA_value = spearman_correlation(mRDMvec, RDMvec)
            
            # save RSA value
            RSA[x_dim,y_dim,z_dim] = RSA_value;
            '''
        else:
            print('Voxel not in ROI \n')      


    # Sort images by object category
    #labels_sorted = labels.sort_values('labels')
    #bold_sorted = bold.get_fdata()[:, :, :, labels_sorted.index]
    
    # ------------------Make image of RSA values in ROI-----------
    
    # Pack the new data inside a Nift1Image using the same affine transform as
    # the original BOLD image
    RSA_plotting = nib.Nifti1Image(RSA, bold.affine)
    
    nil.plotting.plot_glass_brain(RSA_plotting)
    
main()
