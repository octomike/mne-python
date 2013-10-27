"""Data and Channel Location Equivalence Tests"""

# Author: Teon Brooks <teon@nyu.edu>
#
# License: BSD (3-clause)

import os.path as op
import inspect
from numpy.testing import assert_array_almost_equal, assert_array_equal
import scipy.io
from mne.utils import _TempDir
from mne.fiff import Raw, pick_types
from mne.fiff.edf import read_raw_edf

FILE = inspect.getfile(inspect.currentframe())
data_dir = op.join(op.dirname(op.abspath(FILE)), 'data')
hpts_path = op.join(data_dir, 'biosemi.hpts')
bdf_path = op.join(data_dir, 'test.bdf')
matlab_path = op.join(data_dir, 'test_eeglab.mat')

tempdir = _TempDir()


def test_data():
    """Test reading raw edf files
    """
    raw_py = read_raw_edf(bdf_path, n_eeg=72, hpts=hpts_path, preload=True)
    picks = pick_types(raw_py.info, meg=False, eeg=True, exclude='bads')
    data_py, _ = raw_py[picks]

    # this .mat was generated using the EEG Lab Biosemi Reader
    raw_eeglab = scipy.io.loadmat(matlab_path)
    raw_eeglab = raw_eeglab['data'] * 1e-6  # data are stored in microvolts
    data_eeglab = raw_eeglab[picks]

    assert_array_almost_equal(data_py, data_eeglab, decimal=6)


def test_read_segment():
    """Test writing raw edf files when preload is False
    """
    raw1 = read_raw_edf(bdf_path, n_eeg=72, hpts=hpts_path, preload=False)
    raw1_file = op.join(tempdir, 'raw1.fif')

    raw1.save(raw1_file, overwrite=True)
    raw2 = read_raw_edf(bdf_path, n_eeg=72, hpts=hpts_path, preload=True)
    raw2_file = op.join(tempdir, 'raw2.fif')
    raw2.save(raw2_file, overwrite=True)

    raw1 = Raw(raw1_file, preload=True)
    raw2 = Raw(raw2_file, preload=True)
    assert_array_equal(raw1._data, raw2._data)
