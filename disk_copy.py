import sqlite3

from log_utils import bladebit_manager_logger, INFO, WARNING, FAILED, SUCCESS


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


def start_copy():
    bladebit_manager_logger.log(INFO, "Going to start plot manager")
    plot_name = "plot-k32-c05-2023-08-29-13-32-ca00fdcc14deebead979f44fd7f47b38a101d1ee87739f2907deabcf007fa67a.plot"
    insert_new_plot(plot_name, "/mnt/nveme1")
    bladebit_manager_logger.log(WARNING, get_plot_by_name(plot_name))
    update_plot_by_name(plot_name, '/mnt/hydras01', 'in_progess')
    bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
    update_plot_by_name(plot_name, '/mnt/hydras01', 'done')
    bladebit_manager_logger.log(WARNING, get_plot_status_by_name(plot_name))
