# %%
from statistics import stdev
from unicodedata import decimal
import pandas as pd
import numpy as np

from nilearn import plotting
import nibabel as nib

from scipy import signal, stats

import matplotlib.pyplot as plt
import seaborn as sns

import warnings
# %%

def standardize_data(dta):

    """
    Standardizes and detrends the data
    
    Parameters
    ----------
    dta : array_like
        The input data
    
    Returns
    -------
    temp : ndarray
        z-score of the input data.
    
    """
    ret = np.round(signal.detrend(dta,type='linear'),decimals = 6)
    return(ret)

# %%
### THESE ARE PARAMETERS FOR THE MAIN FUNCTION!
# main function will be created after I understood what should I do :D 
#VARIABLES:

data_dir = ''

bold_dta_path = 'subj1/bold.nii.gz'
mask_path = 'subj1/mask4_vt.nii.gz'
label_path = 'subj1/labels.txt'

# %%

bold = nib.load(data_dir + bold_dta_path)
mask = nib.load(data_dir + mask_path)


# Masking the data

# voxels_in_roi = bold.get_fdata()[mask.get_fdata() == 1, :]

labeled_df = pd.read_csv(data_dir + label_path, sep=' ')
labeled_df = labeled_df.reset_index().groupby(['labels','chunks']).agg({'index':list}).reset_index()

# %%
bold_array = bold.get_fdata()


for chunk in range(len(labeled_df)):
    bold_array[:,:,:,labeled_df.loc[chunk,'index']] = \
        standardize_data(bold_array[:,:,:,labeled_df.loc[chunk,'index']])

bold_array = np.apply_along_axis(stats.zscore, 0,\
    bold_array[mask.get_fdata() == 1, :])

# %%

dis_matrix=1-pd.DataFrame(bold_array).corr().values
# %%


plt.figure(figsize=(15,15))

plt.imshow(dis_matrix, cmap='cool')

plt.show()



# %%
