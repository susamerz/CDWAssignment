from pathlib import Path

import numpy as np
import pandas as pd
import nibabel as nib


class BrainData:
    """Class encapsulating brain data.

    This class encapsulates the relevant contents of
    file like `subj1-2010.01.14.tar.gz`.
    """
    def __init__(self, data, chunks, labels, mask, affine):
        assert data.shape[-1] == len(chunks) == len(labels)
        assert data.shape[:-1] == mask.shape
        self.data = data
        self.chunks = chunks
        self.labels = labels
        self.mask = mask
        self.affine = affine

    @classmethod
    def from_directory(cls, dpath, *,
                       apply_mask=True,
                       exclude_labels=['rest', 'scrambledpix']):
        """Initialize object from directory.

        Parameters
        ----------
        dpath:
            Path to the directory
        apply_mask:
            If true, discard all data outside the mask
        exclude_labels:
            Discard data corresponding to these labels
        """
        dpath = Path(dpath)
        bold = nib.load(dpath / 'bold.nii.gz')
        affine = bold.affine
        data = bold.get_fdata()
        mask = nib.load(dpath / 'mask4_vt.nii.gz').get_fdata()
        mask = np.array(mask, dtype=bool)
        if apply_mask:
            data = data[mask == 1]
            mask = np.ones(data.shape[:-1], dtype=bool)
        labels = pd.read_csv(dpath / 'labels.txt', sep=' ')
        chunks = np.array(labels.chunks)
        labels = np.array(labels.labels, dtype=str)

        # Filter labels
        flt = [label not in exclude_labels for label in labels]
        data = data[..., flt]
        chunks = chunks[flt]
        labels = labels[flt]

        return cls(data=data, chunks=chunks, labels=labels,
                   mask=mask, affine=affine)

    @classmethod
    def from_npz_file(cls, fpath):
        """Initialize object from npz file.

        Parameters
        ----------
        fpath:
            Path to the file created with `write()`
        """
        npz = np.load(fpath)
        return cls(data=npz['data'],
                   chunks=npz['chunks'],
                   labels=npz['labels'],
                   mask=npz['mask'],
                   affine=npz['affine'],
                   )

    def write(self, fpath):
        """Write object to a npz file.

        Parameters
        ----------
        fpath:
            Path to the file to be written
        """
        np.savez(fpath,
                 data=self.data,
                 chunks=self.chunks,
                 labels=self.labels,
                 mask=self.mask,
                 affine=self.affine,
                 )

    def sort_by_labels(self):
        """Sort data by its labels.

        This changes the state of the object.
        """
        s_t = np.argsort(self.labels)
        self.data = self.data[..., s_t]
        self.chunks = self.chunks[s_t]
        self.labels = self.labels[s_t]

    def plot_brain(self, index=0):
        """Plot the object's data.

        Parameters
        ----------
        index:
            The time-series index of the volumetric data
        """
        assert self.data.ndim == 4
        from nilearn import plotting
        image = nib.Nifti1Image(self.data[..., index], self.affine)
        plotting.plot_glass_brain(image)
