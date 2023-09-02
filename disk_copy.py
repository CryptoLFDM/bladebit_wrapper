import shutil
import sqlite3
import os

from config import config, chia_const
from log_utils import bladebit_manager_logger, INFO, WARNING, FAILED, SUCCESS
from utils import get_disk_info
# import multiprocessing
# import time


con = sqlite3.connect("plot.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS plots(plot_name TEXT UNIQUE, source TEXT, dest TEXT, status TEXT)")


def insert_new_plot(plot_name: str, source: str):
    query = "INSERT INTO plots(plot_name, source, dest, status) VALUES (?, ?, null, null)"
    values = (plot_name, source)
    try:
        cur.execute(query, values)
        con.commit()
        bladebit_manager_logger.log(SUCCESS, 'plot {} added into plot manager'.format(plot_name))
    except sqlite3.IntegrityError:
        bladebit_manager_logger.log(FAILED, 'plot {} already exists in plot manager'.format(plot_name))


def get_plot_by_name(plot_name: str):
    query = "SELECT * FROM plots WHERE plot_name=?"
    cur.execute(query, (plot_name,))
    return cur.fetchall()


def get_plot_status_by_name(plot_name: str):
    query = "SELECT status FROM plots WHERE plot_name=?"
    cur.execute(query, (plot_name,))
    return cur.fetchall()


def update_plot_by_name(plot_name: str, dest: str, status: str):
    cur.execute("UPDATE plots SET dest=?, status=? WHERE plot_name=?", (dest, status, plot_name))
    con.commit()
    bladebit_manager_logger.log(SUCCESS, 'updated plot {} with status {} and dest {}'.format(plot_name, status, dest))


def left_space_on_directories_to_plots(disk_path: str) -> bool:
    _, _, free = get_disk_info(disk_path)
    if free / chia_const[config['compression_level']]['gib'] > 2:
        return True
    return False


def scan_plots():
    for staging_dir in config['staging_directories']:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.plot'):

                insert_new_plot(filename, staging_dir)


def start_copy():
    bladebit_manager_logger.log(INFO, "Going to start plot manager")
    dest_dir = config['directories_to_plot']
    while(left_space_on_directories_to_plots(dest_dir)):
        scan_plots()
        cur.execute("SELECT * FROM plots WHERE status IS NULL")
        results = cur.fetchall()
        for result in results:
            plot_name = result[0]
            source = result[1]
            bladebit_manager_logger.log(WARNING, get_plot_by_name(plot_name))
            current_dest = dest_dir.pop(0) if dest_dir else None
            if current_dest: #je pense que à partir d'ici j'ai tout à revoir mais que avant je suis correct
                update_plot_by_name(plot_name, current_dest, 'in_progess')
                source_path = os.path.join(source, plot_name)
                dest_path = os.path.join(current_dest, plot_name)
                shutil.move(source_path, dest_path)
                bladebit_manager_logger.log(INFO, f"Moved {plot_name} from {source_path} to {dest_path}")
                bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
                update_plot_by_name(plot_name, current_dest, 'done')
            bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))