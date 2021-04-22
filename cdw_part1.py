import numpy as np
import pandas as pd
import matplotlib as mp
import scipy as sc
import nibabel as nib
import nilearn as nil

def preprocess(chunks):
    for chunk in chunks:
        for x_dim in chunk.shape[0]:
            for y_dim in chunk.shape[1]:
                for z_dim in chunk.shape[2]:
                    # now we have one voxel timeseries
                    # remove linear trend and z-score the data
                    
                    voxel_ts = chunk[x_dim, y_dim, z_dim, :]
                    voxel_ts_detrend = sc.signal.detrend(voxel_ts)
                    voxel_ts_processed = sc.stats.zscore(voxel_ts_detrend)
                    

def main():

    bold = nib.load('subj1/bold.nii.gz')
    
    mask = nib.load('subj1/mask4_vt.nii.gz')
    voxels_in_roi = bold.get_fdata()[mask.get_fdata() == 1, :]    
    anat = nib.load('subj1/anat.nii.gz')
    
    labels = pd.read_csv('subj1/labels.txt', sep=' ')
    
    # make 5-dimensional numpy array for chunk data
    # size 40x64x64x[time_length_of_chunk]x11
    chunks = [];
    
    for i in range(11):
        labels_chunk = labels.query('chunks == %d' % (i))
        bold_chunk = bold.get_fdata()[:, :, :, labels_chunk.index]
        chunks.append(bold_chunk)
        
    chunks_np = np.array(chunks)
    
    # pre-process all chunks
    chunks_np_pp = preprocess(chunks_np)
    
    
    # make searchlights around each voxel --> loop through voxels and make
    # searchlight centering on each
    
    # compute RDM for each searchlight (needs data from all 11 chunks)
    # compare to model RDM --> get RSA value for center voxel
    
    # make image of RSA values in ROI

main()