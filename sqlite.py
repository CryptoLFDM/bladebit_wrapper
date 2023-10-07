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

    def get_plot_by_name(self, plot_name: str) -> list:
        query = "SELECT * FROM plots WHERE plot_name=?"
        return self._execute_query(query, (plot_name,))

    def insert_new_plot(self, plot_name: str, source: str, timestamp: float = datetime.now().timestamp()) -> list:
        if not self.get_plot_by_name(plot_name):
            query = "INSERT INTO plots(plot_name, source, dest, status, timestamp) VALUES (?, ?, null, null, ?)"
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
        values = (None, None, 'in_progress')
        return self._execute_query(query, values)

    def get_first_plot_without_status(self) -> list:
        query = "SELECT * FROM plots WHERE status IS NULL ORDER BY timestamp ASC LIMIT 1"
        return self._execute_query(query)

    def drop_table(self) -> list:
        query = "DROP TABLE IF EXISTS plots"
        return self._execute_query(query)

    def count_raw(self) -> list:
        query = "SELECT COUNT(*) FROM plots;"
        return self._execute_query(query)

    def get_all_plots(self) -> list:
        query = "SELECT * FROM plots;"
        return self._execute_query(query)

    def get_n_first_plot_without_status(self, batch_size: int) -> list:
        query = "SELECT * FROM plots WHERE status IS NULL ORDER BY timestamp ASC LIMIT {}".format(batch_size)
        return self._execute_query(query)

    def get_plot_destination_by_name(self, plot_name: str) -> list:
        query = "SELECT dest FROM plots WHERE plot_name=?"
        return self._execute_query(query, (str(plot_name),))

    def get_all_destination_by_status(self, status: str) -> list:
        query = "SELECT dest FROM plots WHERE status=?"
        return self._execute_query(query, (str(status),))