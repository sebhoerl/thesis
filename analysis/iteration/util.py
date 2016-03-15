import builder
import sqlite3

class DatabaseTask:
    def __init__(self, db_path):
        self.db_path = db_path

    def check_table_exists(self, table):
        with self.get_connection() as connection:
            return connection.execute("""
                select name from sqlite_master where type="table" and name="%s"
            """ % table).fetchone() is not None

    def drop_if_exists(self, table):
        with self.get_connection() as connection:
            connection.execute("""
                drop table if exists %s
            """ % table)

    def get_connection(self):
        return sqlite3.connect(self.db_path)
