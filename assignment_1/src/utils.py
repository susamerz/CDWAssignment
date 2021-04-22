from pathlib import Path

import numpy as np
import pandas as pd
import nibabel as nib


class BrainData:
    """Class encapsulating brain data.

    This class encapsulates the relevant contents of
    file like `subj1-2010.01.14.tar.gz`.
    """
    def __init__(self, data, chunks, labels):
        self.data = data
        self.chunks = chunks
        self.labels = labels

    @classmethod
    def from_directory(cls, dpath, *,
                       mask=True,
                       exclude_labels=['rest', 'scrambledpix']):
        dpath = Path(dpath)
        bold = nib.load(dpath / 'bold.nii.gz')
        data = bold.get_fdata()
        if mask:
            mask_data = nib.load(dpath / 'mask4_vt.nii.gz').get_fdata()
            data = data[mask_data == 1]
        labels = pd.read_csv(dpath / 'labels.txt', sep=' ')
        chunks = np.array(labels.chunks)
        labels = np.array(labels.labels, dtype=str)

        # Filter labels
        flt = [label not in exclude_labels for label in labels]
        data = data[:, flt]
        chunks = chunks[flt]
        labels = labels[flt]

        return cls(data=data, chunks=chunks, labels=labels)

    @classmethod
    def from_npz_file(cls, fpath):
        npz = np.load(fpath)
        return cls(data=npz['data'],
                   chunks=npz['chunks'],
                   labels=npz['labels'])

    def write(self, fpath):
        np.savez(fpath,
                 data=self.data,
                 chunks=self.chunks,
                 labels=self.labels)

    def sort_by_labels(self):
        """Sort data by its labels."""
        s_t = np.argsort(self.labels)
        self.data = self.data[..., s_t]
        self.chunks = self.chunks[s_t]
        self.labels = self.labels[s_t]
