import unittest
import os
from pathlib import Path
import touch
import string
import random
import logging
import sys
import shutil
from unittest.mock import patch, Mock
from datetime import datetime

import disk_copy
import sqlite
import config_loader
import log_utils


def get_random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def create_struct(directory: str, nbr_plot: int):
    if not os.path.isdir(Path(directory)):
        os.mkdir(Path(directory))
    for i in range(nbr_plot):
        file = open(Path('{}/plot-k32-c05-2023-09-03-20-59-{}.plot'.format(directory, get_random_string(65))), 'w')
        file.write('')
        file.close()


def prepare_test():
    if not os.path.isdir(Path('tests/fake_disk')):
        os.makedirs(Path('tests/fake_disk'))
    create_struct('tests/fake_disk/Source_A', 10)
    create_struct('tests/fake_disk/Source_B', 5)
    create_struct('tests/fake_disk/Dest_A', 0)
    create_struct('tests/fake_disk/Dest_B', 0)
    create_struct('tests/fake_disk/Dest_C', 0)
    create_struct('tests/fake_disk/Dest_D', 0)


def clean_test():
    shutil.rmtree(Path('tests/fake_disk/'), ignore_errors=True)
    if os.path.exists('plot.db'):
        os.remove('plot.db')
    else:
        print("The file does not exist")


class TestScanPlots(unittest.TestCase):
    clean_test()
    prepare_test()

    def test_insert_plots(self):
        # Set up the custom logger with debug mode off
        log_utils.init_logger(debug=False)
        staging_dir = ['tests/fake_disk/Source_A', 'tests/fake_disk/Source_B']
        pool_path = 'plot.db'
        sample = []
        for path in staging_dir:
            plots = os.listdir(path)
            for plot in plots:
                sample.append((plot, path, None, None, None))
        with patch('config_loader.Config', Mock(**{
            'directories_to_plot': ['tests/fake_disk/Dest_A', 'tests/fake_disk/Dest_B', 'tests/fake_disk/Dest_C', 'tests/fake_disk/Dest_D'],
            'use_staging_directories': True,
            'staging_directories': staging_dir
        })):
            disk_copy.scan_plots()

            DBPool = sqlite.DBPool(pool_path)
            res = DBPool.get_all_plots()
            self.assertPlotsEqual(sorted(sample, key=lambda a: a[0]), sorted(res, key=lambda a: a[0]))

    def assertPlotsEqual(self, sample, res):
        self.assertEqual(len(sample), len(res))
        for item1, item2 in zip(sample, res):
            self.assertEqual(item1[0], item2[0])



if __name__ == '__main__':
    clean_test()
    config_loader.load_config('config/config.yml')
    prepare_test()
    unittest.main()
    clean_test()
