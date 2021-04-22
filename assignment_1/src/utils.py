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
    def from_directory(cls, dpath):
        dpath = Path(dpath)
        bold = nib.load(dpath / 'bold.nii.gz')
        labels = pd.read_csv(dpath / 'labels.txt', sep=' ')
        return cls(data=bold.get_fdata(),
                   chunks=np.array(labels.chunks),
                   labels=np.array(labels.labels))
