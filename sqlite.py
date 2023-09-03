import sqlite3
import threading


class DBPool:
    db_file = 'plot.db'

    def __init__(self):
        self.lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        con = sqlite3.connect(self.db_file)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS plots(plot_name TEXT UNIQUE, source TEXT, dest TEXT, status TEXT)")
        con.commit()
        con.close()

    def _execute_query(self, query, values=None):
        with self.lock:
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
                # Handle the error here
                pass
            finally:
                con.close()

    def get_plot_by_name(self, plot_name):
        query = "SELECT * FROM plots WHERE plot_name=?"
        return self._execute_query(query, (plot_name,))

    def insert_new_plot(self, plot_name, source):
        if not self.get_plot_by_name(plot_name):
            query = "INSERT INTO plots(plot_name, source, dest, status) VALUES (?, ?, null, null)"
            values = (plot_name, source)
            self._execute_query(query, values)

    def get_plot_status_by_name(self, plot_name):
        query = "SELECT status FROM plots WHERE plot_name=?"
        return self._execute_query(query, (plot_name,))

    def update_plot_by_name(self, plot_name, dest, status):
        query = "UPDATE plots SET dest=?, status=? WHERE plot_name=?"
        values = (dest, status, plot_name)
        self._execute_query(query, values)

    def ensure_db_has_not_in_progess_plot_at_start_up(self):
        query = "UPDATE plots SET status=NULL, dest=NULL WHERE status='in_progress'"
        self._execute_query(query)

    def get_first_plot_without_status(self):
        query = "SELECT * FROM plots WHERE status IS NULL LIMIT 1"
        return self._execute_query(query)
