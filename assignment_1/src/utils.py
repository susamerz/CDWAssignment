from pathlib import Path
import pandas as pd
import nibabel as nib


class BrainData:
    """Class encapsulating brain data.

    This class encapsulates the relevant contents of
    file like `subj1-2010.01.14.tar.gz`.
    """
    def __init__(self, dpath):
        self._dpath = Path(dpath)
        self._bold = nib.load(self._dpath / 'bold.nii.gz')
        self._labels = pd.read_csv(self._dpath / 'labels.txt', sep=' ')

    @property
    def data(self):
        return self._bold.get_fdata()

    @property
    def chunks(self):
        return self._labels.chunks

    @property
    def labels(self):
        return self._labels.labels
