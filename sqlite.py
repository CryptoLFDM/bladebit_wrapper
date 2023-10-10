import sqlite3
import threading
from datetime import datetime
import log_utils as wp


class DBPool:
    def __init__(self, db_filename: str):
        self.db_file = db_filename
        self.lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        con = sqlite3.connect(self.db_file)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS plots(plot_name TEXT UNIQUE, source TEXT, dest TEXT, status TEXT, timestamp TIMESTAMP)")
        con.commit()
        con.close()

    def _execute_query(self, query: str, values=None) -> list:
        with self.lock:
            self._create_table()
            con = sqlite3.connect(self.db_file)
            cur = con.cursor()
            try:
                if values:
                    cur.execute(query, values)
                else:
                    cur.execute(query)
                con.commit()
                return cur.fetchall()
            except sqlite3.Error as e:
                wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, str(e))
                # Handle the error here
                pass
            finally:
                con.close()

    def _safe_read_and_update_value(self, select_query: str):
        with self.lock:
            try:
                con = sqlite3.connect(self.db_file)
                cursor = con.cursor()

                cursor.execute(select_query)
                current_value = cursor.fetchone()

                if current_value:
                    plot_name, _, _, _, _ = current_value
                    update_query = "UPDATE plots SET status='{}' WHERE plot_name='{}'".format('in_progress', plot_name)

                    cursor.execute(update_query)
                    con.commit()
                    return plot_name
            except sqlite3.Error as e:
                wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, str(e))
                pass
            finally:
                con.close()

    def _safe_insert_if_not_exist(self, plot_name: str, source: str, timestamp: float):
        with self.lock:
            try:
                con = sqlite3.connect(self.db_file)
                cursor = con.cursor()

                cursor.execute("SELECT * FROM plots WHERE plot_name='{}'".format(plot_name))
                current_value = cursor.fetchone()

                if current_value is None:
                    query = "INSERT INTO plots(plot_name, source, dest, status, timestamp) VALUES (?, ?, null, 'to_process', ?)"
                    values = (str(plot_name), str(source), timestamp)
                    cursor.execute(query, values)
                    con.commit()
                    return True
            except sqlite3.Error as e:
                wp.Logger.bladebit_manager_logger.log(wp.Logger.FAILED, str(e))
            finally:
                con.close()

    def get_plot_by_name(self, plot_name: str) -> list:
        query = "SELECT * FROM plots WHERE plot_name=?"
        return self._execute_query(query, (plot_name,))

    def insert_new_plot(self, plot_name: str, source: str, timestamp: float = datetime.now().timestamp()) -> list:
        if not self.get_plot_by_name(plot_name):
            query = "INSERT INTO plots(plot_name, source, dest, status, timestamp) VALUES (?, ?, null, 'to_process', ?)"
            values = (str(plot_name), str(source), timestamp)
            return self._execute_query(query, values)

    def get_plot_status_by_name(self, plot_name: str) -> list:
        query = "SELECT status FROM plots WHERE plot_name=?"
        return self._execute_query(query, (str(plot_name),))

    def update_plot_by_name(self, plot_name: str, dest: str, status: str) -> []:
        query = "UPDATE plots SET dest=?, status=? WHERE plot_name=?"
        values = (dest, str(status), str(plot_name))
        return self._execute_query(query, values)

    def ensure_db_has_not_in_progess_plot_at_start_up(self) -> list:
        query = "UPDATE plots SET status=?, dest=? WHERE status=?"
        values = ('to_process', None, 'in_progress')
        return self._execute_query(query, values)

    def get_first_plot_without_status(self) -> list:
        query = "SELECT * FROM plots WHERE status=? ORDER BY timestamp ASC LIMIT 1"
        values = ('to_process',)
        return self._execute_query(query, values)

    def drop_table(self) -> list:
        query = "DROP TABLE IF EXISTS plots"
        return self._execute_query(query)

    def count_raw(self) -> list:
        query = "SELECT COUNT(*) FROM plots;"
        return self._execute_query(query)

    def get_all_plots(self) -> list:
        query = "SELECT * FROM plots;"
        return self._execute_query(query)

    def get_plot_destination_by_name(self, plot_name: str) -> list:
        query = "SELECT dest FROM plots WHERE plot_name=?"
        return self._execute_query(query, (str(plot_name),))

    def get_all_destination_by_status(self, status: str) -> list:
        query = "SELECT dest FROM plots WHERE status=?"
        return self._execute_query(query, (str(status),))

    def get_first_plot_without_status_and_change_status(self) -> str:
        select_query = "SELECT * FROM plots WHERE status='{}' ORDER BY timestamp ASC LIMIT 1".format('to_process')
        return self._safe_read_and_update_value(select_query)

    def insert_new_plot_if_not_exist(self, plot_name: str, source: str, timestamp: float = datetime.now().timestamp()) -> bool:
        return self._safe_insert_if_not_exist(plot_name, source, timestamp)