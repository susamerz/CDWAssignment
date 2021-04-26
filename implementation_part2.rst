.. warning::
    The analysis pipeline described below takes very inappropriate shortcuts to save time.
    Do not use this analysis pipeline in an actual study!

==============================================
Day 2, part 2: Extending the analysis pipeline
==============================================

For the second part, we will extend the analysis pipeline with a group level analysis.
The data for all six subjects can be downloaded from: http://data.pymvpa.org/datasets/haxby2001/.
Each subject has their own ROI defined (``subj#/mask4_vt.nii.gz``).
Perform the searchlight RSA analysis for each subject and then perform a group level analysis.

The group level analysis will simply be to compute the mean of the RSA values across the subjects.
The MRI images come from different brains, and therefore do not necessarily match. However, they are sort of aligned already and to keep the assignment possible to do in a short time, we will not perform any more aligning of the images.
However, since each subject has their own ROI, the ROIs will not match perfectly.
Perform the group level analysis on all voxels that are part of all at least one subject's ROI.
When computing the grand average RSA value for a voxel, treat any subject for which the voxel is not part of their ROI as having an RSA value of zero for this voxel.


Office hour, in case you have any questions, or are stuck, Wednesday and Thursday at 14:00 in the workshops Zoom 

