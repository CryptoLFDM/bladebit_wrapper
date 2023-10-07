import unittest
import os
from pathlib import Path
import string
import random
import shutil
from unittest.mock import patch, Mock

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
    log_utils.init_logger(debug=False)

    def test_1_scan_plots(self):
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

    def test_2_move_plot(self):
        staging_dir = ['tests/fake_disk/Source_A', 'tests/fake_disk/Source_B']
        directories_to_plot = ['tests/fake_disk/Dest_A', 'tests/fake_disk/Dest_B', 'tests/fake_disk/Dest_C', 'tests/fake_disk/Dest_D']
        pool_path = 'plot.db'
        with patch('config_loader.Config', Mock(**{
            'directories_to_plot': directories_to_plot,
            'use_staging_directories': True,
            'staging_directories': staging_dir
        })):
            DBPool = sqlite.DBPool(pool_path)
            first_plot = DBPool.get_first_plot_without_status()
            check = disk_copy.move_plot(first_plot[0][0], staging_dir[0], directories_to_plot[0])
            self.assertEqual(True, check)
            plots = os.listdir('tests/fake_disk/Dest_A')
            self.assertEqual(plots[0], first_plot[0][0])
            status = DBPool.get_plot_status_by_name(first_plot[0][0])
            self.assertEqual([('done',)], status)

    def test_3_get_first_free_destination(self):
        staging_dir = ['tests/fake_disk/Source_A', 'tests/fake_disk/Source_B']
        directories_to_plot = ['tests/fake_disk/Dest_A', 'tests/fake_disk/Dest_B', 'tests/fake_disk/Dest_C', 'tests/fake_disk/Dest_D']
        pool_path = 'plot.db'
        with patch('config_loader.Config', Mock(**{
            'directories_to_plot': directories_to_plot,
            'use_staging_directories': True,
            'staging_directories': staging_dir
        })):
            DBPool = sqlite.DBPool(pool_path)
            res = DBPool.get_all_plots()

            DBPool.update_plot_by_name(res[0][0], directories_to_plot[0], 'in_progress')
            DBPool.update_plot_by_name(res[1][0], directories_to_plot[1], 'in_progress')
            first_dest = disk_copy.get_first_free_destination()
            self.assertEqual('tests/fake_disk/Dest_C', first_dest)

            DBPool.update_plot_by_name(res[2][0], directories_to_plot[2], 'in_progress')
            second_dest = disk_copy.get_first_free_destination()
            self.assertEqual('tests/fake_disk/Dest_D', second_dest)

            DBPool.update_plot_by_name(res[3][0], directories_to_plot[3], 'in_progress')
            third_dest = disk_copy.get_first_free_destination()
            self.assertEqual(None, third_dest)

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
