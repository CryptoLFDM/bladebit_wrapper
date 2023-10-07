import unittest
import os
from datetime import datetime

import sqlite


class SqliteTest(unittest.TestCase):
    try:
        os.remove('tests/test_plot.db')
        print(f'File tests/test_plot.db deleted successfully.')
    except OSError:
        print(f'tests/test_plot.db does not exist')

    def test_get_all_destination_by_status(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.update_plot_by_name(plot_name='random.plot', dest='/mnt/moon', status='in_progress')
        clock2 = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='alpha.plot', source='/mnt/imaginarium', timestamp=clock2)
        clock3 = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='beta.plot', source='/mnt/imaginarium', timestamp=clock3)
        DBPool.update_plot_by_name(plot_name='beta.plot', dest='/mnt/jupyter', status='in_progress')
        res = DBPool.get_all_destination_by_status('in_progress')
        self.assertEqual([('/mnt/moon',), ('/mnt/jupyter',)], res)
        DBPool.drop_table()

    def test_doubleBDD(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.insert_new_plot(plot_name='alpha.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.insert_new_plot(plot_name='beta.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool2 = sqlite.DBPool('tests/test_plot.db')
        res = DBPool2.get_all_plots()
        self.assertEqual([('random.plot', '/mnt/imaginarium', None, None, clock),
                          ('alpha.plot', '/mnt/imaginarium', None, None, clock),
                          ('beta.plot', '/mnt/imaginarium', None, None, clock)], res)
        DBPool.drop_table()

    def test_count_raw(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.insert_new_plot(plot_name='alpha.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.insert_new_plot(plot_name='beta.plot', source='/mnt/imaginarium', timestamp=clock)
        res = DBPool.count_raw()
        self.assertEqual([(3,)], res)
        DBPool.drop_table()

    def test_ensure_db_has_not_in_progess_plot_at_start_up(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.update_plot_by_name(plot_name='random.plot', dest='/mnt/moon', status='in_progress')
        DBPool.insert_new_plot(plot_name='alpha.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.insert_new_plot(plot_name='beta.plot', source='/mnt/imaginarium', timestamp=clock)
        res = DBPool.get_all_plots()
        self.assertEqual([('random.plot',
                           '/mnt/imaginarium',
                           '/mnt/moon',
                           'in_progress',
                           clock),
                          ('alpha.plot', '/mnt/imaginarium', None, None, clock),
                          ('beta.plot', '/mnt/imaginarium', None, None, clock)], res)

        _ = DBPool.ensure_db_has_not_in_progess_plot_at_start_up()
        res = DBPool.get_all_plots()
        self.assertEqual([('random.plot', '/mnt/imaginarium', None, None, clock),
                          ('alpha.plot', '/mnt/imaginarium', None, None, clock),
                          ('beta.plot', '/mnt/imaginarium', None, None, clock)], res)
        DBPool.drop_table()

    def test_get_first_plot_without_status(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.update_plot_by_name(plot_name='random.plot', dest='/mnt/moon', status='in_progress')
        clock2 = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='alpha.plot', source='/mnt/imaginarium', timestamp=clock2)
        clock3 = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='beta.plot', source='/mnt/imaginarium', timestamp=clock3)
        res = DBPool.get_first_plot_without_status()
        self.assertEqual([('alpha.plot', '/mnt/imaginarium', None, None, clock2)], res)
        DBPool.drop_table()

    def test_get_plot_status_by_name(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        DBPool.update_plot_by_name(plot_name='random.plot', dest='/mnt/moon', status='in_progress')
        _ = DBPool.get_plot_by_name('random.plot')
        res = DBPool.get_plot_status_by_name(plot_name='random.plot')
        self.assertEqual([('in_progress',)], res)
        DBPool.drop_table()

    def test_update_bdd(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        _ = DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        _ = DBPool.update_plot_by_name(plot_name='random.plot', dest='/mnt/moon', status='in_progress')
        res = DBPool.get_plot_by_name('random.plot')
        self.assertEqual([('random.plot', '/mnt/imaginarium', '/mnt/moon', 'in_progress', clock)], res)
        DBPool.drop_table()

    def test_insert_bdd(self):
        DBPool = sqlite.DBPool('tests/test_plot.db')
        clock = datetime.now().timestamp()
        _ = DBPool.insert_new_plot(plot_name='random.plot', source='/mnt/imaginarium', timestamp=clock)
        res = DBPool.get_plot_by_name('random.plot')
        self.assertEqual([('random.plot', '/mnt/imaginarium', None, None, clock)], res)
        DBPool.drop_table()


if __name__ == '__main__':
    unittest.main()
