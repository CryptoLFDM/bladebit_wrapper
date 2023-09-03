import shutil
import sqlite3
import os
import time
import multiprocessing

from config import config
from log_utils import bladebit_manager_logger, INFO, WARNING, FAILED, SUCCESS
from plot import can_plot_at_least_one_plot_safely


con = sqlite3.connect("plot.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS plots(plot_name TEXT UNIQUE, source TEXT, dest TEXT, status TEXT)")


def get_plot_by_name(plot_name: str):
    query = "SELECT * FROM plots WHERE plot_name=?"
    cur.execute(query, (plot_name,))
    return cur.fetchall()


def insert_new_plot(plot_name: str, source: str):
    if get_plot_by_name(plot_name) is not []:
        return
    query = "INSERT INTO plots(plot_name, source, dest, status) VALUES (?, ?, null, null)"
    values = (plot_name, source)
    try:
        cur.execute(query, values)
        con.commit()
        bladebit_manager_logger.log(SUCCESS, 'plot {} added into plot manager'.format(plot_name))
    except sqlite3.Error as e:
        bladebit_manager_logger.log(FAILED, 'Error occurred while inserting plot {}: {}'.format(plot_name, str(e)))


def get_plot_status_by_name(plot_name: str):
    query = "SELECT status FROM plots WHERE plot_name=?"
    cur.execute(query, (plot_name,))
    return cur.fetchall()


def update_plot_by_name(plot_name: str, dest: str, status: str):
    cur.execute("UPDATE plots SET dest=?, status=? WHERE plot_name=?", (dest, status, plot_name))
    con.commit()
    bladebit_manager_logger.log(SUCCESS, 'updated plot {} with status {} and dest {}'.format(plot_name, status, dest))


def left_space_on_directories_to_plots():
    for disk in config['directories_to_plot']:
        if can_plot_at_least_one_plot_safely(disk):
            return True
    return False


def scan_plots():
    for staging_dir in config['staging_directories']:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.plot'):
                insert_new_plot(filename, staging_dir)

def reset_in_progess_plots_boot():
    cur.execute("UPDATE plots SET status=NULL WHERE status='in_progress'")
    con.commit()


def process_plots(destination):
    while left_space_on_directories_to_plots():
        scan_plots()
        try:
            cur.execute("SELECT * FROM plots WHERE status IS NULL LIMIT 1")
            result = cur.fetchone()
            if result:
                plot_name, source, _, _ = result
                bladebit_manager_logger.log(WARNING, get_plot_by_name(plot_name))
                update_plot_by_name(plot_name, destination, 'in_progress')
                source_path = os.path.join(source, plot_name)
                dest_path = os.path.join(destination, plot_name)
                shutil.move(source_path, dest_path)
                with multiprocessing.Lock():
                    bladebit_manager_logger.log(INFO, 'Moved {} from {} to {}'.format(plot_name, source, dest_path))
                    bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
                    update_plot_by_name(plot_name, destination, 'done')
                    bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
            else:
                bladebit_manager_logger.log(FAILED, 'Sleep mode for 5 minutes')
                time.sleep(300)
        except Exception as e:
            bladebit_manager_logger.log(FAILED, str(e))
            time.sleep(300)


def start_copy():
    reset_in_progess_plots_boot()
    bladebit_manager_logger.log(INFO, "Going to start plot manager")
    dest_dir = config['directories_to_plot']
    num_process = 5
    processes = []

    for _ in range(num_process):
        if dest_dir:
            destination = dest_dir.pop(0)
            process = multiprocessing.Process(target=process_plots, args=(destination,))
            processes.append(process)
            process.start()

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            process.join()