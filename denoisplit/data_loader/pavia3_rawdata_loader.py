"""
Here, we load the raw data generated by Pezzotti from Pavia (2 channel data which does not have the input channel). 
"""
import os

import numpy as np

from denoisplit.core.custom_enum import Enum
from denoisplit.core.data_split_type import DataSplitType, get_datasplit_tuples
from nd2reader import ND2Reader


class Pavia3SeqPowerLevel(Enum):
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'

    @staticmethod
    def subdir(power_level):
        return {
            Pavia3SeqPowerLevel.High: 'Main',
            Pavia3SeqPowerLevel.Medium: 'Divided_2',
            Pavia3SeqPowerLevel.Low: 'Divided_4'
        }[power_level]


class Pavia3SeqAlpha(Enum):
    Balanced = "Balanced"
    MediumSkew = "MediumSkew"
    HighSkew = "HighSkew"

    @staticmethod
    def subdir(alpha_level):
        return {
            Pavia3SeqAlpha.Balanced: 'Cond_1',
            Pavia3SeqAlpha.MediumSkew: 'Cond_2',
            Pavia3SeqAlpha.HighSkew: 'Cond_3'
        }[alpha_level]


def load_one_file(fpath):
    """
    '/group/jug/ashesh/data/pavia3_sequential/Cond_2/Main/1_002.nd2'
    """
    output = {}
    with ND2Reader(fpath) as fobj:
        for c in range(len(fobj.metadata['channels'])):
            output[c] = []
            for z in fobj.metadata['z_levels']:
                img = fobj.get_frame_2D(c=c, z=z)
                img = img[None, ..., None]
                output[c].append(img)
            output[c] = np.concatenate(output[c], axis=0)
    return np.concatenate([output[0], output[1]], axis=-1)


def load_data(rootdatadir, power_level, alpha_level):
    subdir = os.path.join(rootdatadir, Pavia3SeqAlpha.subdir(alpha_level), Pavia3SeqPowerLevel.subdir(power_level))
    fpaths = []
    for fname in os.listdir(subdir):
        fpath = os.path.join(subdir, fname)
        fpaths.append(fpath)

    fpaths = sorted(fpaths)
    data = [load_one_file(fpath) for fpath in fpaths]
    return np.concatenate(data, axis=0)


def get_train_val_data(dirname, data_config, datasplit_type, val_fraction, test_fraction):
    power_level = data_config.power_level
    alpha_level = data_config.alpha_level
    assert power_level in [Pavia3SeqPowerLevel.High, Pavia3SeqPowerLevel.Medium, Pavia3SeqPowerLevel.Low]
    assert alpha_level in [Pavia3SeqAlpha.Balanced, Pavia3SeqAlpha.MediumSkew, Pavia3SeqAlpha.HighSkew]

    data = load_data(dirname, power_level, alpha_level)
    print(f'Loaded from {dirname} Power:{power_level} Alpha:{alpha_level} Mode:{DataSplitType.name(datasplit_type)}')

    if datasplit_type == DataSplitType.All:
        return data.astype(np.float32)

    train_idx, val_idx, test_idx = get_datasplit_tuples(val_fraction, test_fraction, len(data), starting_test=True)
    if datasplit_type == DataSplitType.Train:
        return data[train_idx].astype(np.float32)
    elif datasplit_type == DataSplitType.Val:
        return data[val_idx].astype(np.float32)
    elif datasplit_type == DataSplitType.Test:
        return data[test_idx].astype(np.float32)


if __name__ == '__main__':
    data = load_data('/group/jug/ashesh/data/pavia3_sequential', Pavia3SeqPowerLevel.High, Pavia3SeqAlpha.Balanced)
    print(data.shape)