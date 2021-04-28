#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Testrunner for checking and plotting, interactive (Spyder)

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-28
@notes:   Fit for testing
"""

import os
from cdw_pipeline import get_rsa_brain, run_group_rsa
from nilearn import plotting

datadir = '/Users/jenska/code/python/_misc/cdw2021/DATA'

#%% Get single RSA brain (with forced calculation)
rsa_brain = get_rsa_brain('subj1', force_rsa_calc=True)
plotting.plot_glass_brain(rsa_brain)

#%% Get grand mean over subjects
subjs = [s for s in os.listdir(datadir) if 'subj' in s]
rsa_grand_mean = run_group_rsa(subjs)

plotting.plot_glass_brain(rsa_grand_mean)

#%%