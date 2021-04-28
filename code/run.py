#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODE DESIGN WORKSHOP 2021
Testrunner for checking stuff, interactive

@author:  jenni.saaristo@helsinki.fi
@version: 2021-04-28
@notes:   
"""

from cdw_pipeline import get_rsa_brain
from nilearn import plotting

#%%
subj = 'subj1'
rsa_brain = get_rsa_brain(subj)

#%%
plotting.plot_glass_brain(rsa_brain)

#%%