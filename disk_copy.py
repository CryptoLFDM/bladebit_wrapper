import shutil
import sqlite3
from config import config
from log_utils import bladebit_manager_logger, INFO, WARNING, FAILED, SUCCESS
import os
import time


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


def scan_plots():
    for staging_dir in config['staging_directories']:
        for filename in os.listdir(staging_dir):
            if filename.endswith('.plot'):
                plot_name = filename
                source = staging_dir

                insert_new_plot(plot_name, source)


def start_copy():
    bladebit_manager_logger.log(INFO, "Going to start plot manager")
    scan_plots()
    cur.execute("SELECT * FROM plots WHERE status IS NULL")
    results = cur.fetchall()
    dest_dir = config['directories_to_plot']
    for result in results:
        plot_name = result[0]
        source = result[1]
        bladebit_manager_logger.log(WARNING, get_plot_by_name(plot_name))
        current_dest = dest_dir.pop(0) if dest_dir else None
        if current_dest:
            update_plot_by_name(plot_name, current_dest, 'in_progess')
            source_path = os.path.join(source, plot_name)
            dest_path = os.path.join(current_dest, plot_name)
            shutil.move(source_path, dest_path)
            bladebit_manager_logger.log(INFO, f"Moved {plot_name} from {source_path} to {dest_path}")
            bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
            update_plot_by_name(plot_name, current_dest, 'done')
        bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
