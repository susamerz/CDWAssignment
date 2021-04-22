# %%
from statistics import stdev
import pandas as pd
import numpy as np

from nilearn import plotting
import nibabel as nib

from obspy.signal.detrend import polynomial
from statsmodels.tsa.stattools import adfuller
from scipy import signal

import matplotlib.pyplot as plt
import seaborn as sns

import warnings
# %%


def detrend_polynomial(dta):
    """
    Remove polynomial trend of the series. This function applies 
    detrending if necessary. Unit-root test statistics used in 
    this function is Augmented Dickey-Fuller.
    
    Parameters
    ----------
    dta : array_like
        The input series
    
    Returns
    -------
    temp : ndarray
        The detrended input series.
    """
    
    # Order starts from 0 (no detrending applied)
    # to 7. Any number more than this causes overfitting
    if adfuller(dta,regression='ct')[1]> 0.05:
        for order in range(0,7):
                temp = polynomial(dta, order=order, plot=False)
                adf_result_ct = adfuller(temp,regression='ct')
                if adf_result_ct[1]<0.05 :
                    return(temp)
                
        warnings.warn('polynomial detrend did not work.')
        return(temp)
    else:
        return(dta)
           
            
def detrend_data(dta):
    """
    Remove trend of the series. This function applies 
    both first differencing and detrending if necessary.
    Unit-root test statistics used in this function is
    Augmented Dickey-Fuller.
    
    Parameters
    ----------
    dta : array_like
        The input series
    
    Returns
    -------
    temp : ndarray
        The detrended input series.
    
    """
    adf_result_c = adfuller(dta,regression='c')
    # checking for unitroot:
    if adf_result_c[1]<0.05 :
        
        # testing and fitting polinomials for detrending
        
        detrend_polynomial(dta)

        return(dta)
        warnings.warn('Data is unchanged')
    else:
        # First differencing the data
        dta = signal.detrend(dta,type ='constant')
        detrend_polynomial(dta)
        return(dta)

def standardize_data(dta):

    """
    Standardizes the data
    
    Parameters
    ----------
    dta : array_like
        The input data
    
    Returns
    -------
    temp : ndarray
        z-score of the input data.
    
    """
    
    mean = np.mean(dta)
    stdev = np.std(dta)
    ret = (dta-mean)/stdev
    return(ret)

# %%


### THESE ARE PARAMETERS FOR THE MAIN FUNCTION!
# main function will be created after I understood what should I do :D 
#VARIABLES:

data_dir = ''

bold_dta_path = 'subj1/bold.nii.gz'
mask_path = 'subj1/mask4_vt.nii.gz'
label_path = 'subj1/labels.txt'

#%%
bold = nib.load(data_dir + bold_dta_path)
mask = nib.load(data_dir + mask_path)
labeled_df = pd.read_csv(data_dir + label_path, sep=' ')

# Masking the data

voxels_in_roi = bold.get_fdata()[mask.get_fdata() == 1, :]

# producing a dataframe with columns for each voxel.

labeled_df['voxel'] = pd.Series(list(voxels_in_roi.T))
labeled_df = labeled_df.drop('voxel',axis=1).join(pd.DataFrame(labeled_df['voxel'].to_list()))

## detrending the voxels

for label in labeled_df.labels.unique():
    for col in range(len(labeled_df.columns)-2):
        labeled_df.loc[labeled_df['labels'] == label,col] = \
                detrend_data(labeled_df.loc[labeled_df['labels'] == label,col])
print('detrending is done!')

# %%

### HERE IS WHERE I HAVE PROBLEM
'''
I did not fully understood whta I need to do to produce a model RDM.
So far I detrended every voxel time series for same object across all chunks. 
Then I calculated the pairwise correlation between all images. 

Also I could not plot it since I ran out of RAM :D
even masking data befor analysis did not solve the solution.


'''
# spearman pairwise correlation:

RDM_BOLD = 1-labeled_df\
    .reset_index()\
        .groupby(['labels','chunks','index'])\
            .first().T.corr('pearson')


















# %%
