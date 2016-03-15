import builder
import util
import gzip
import xml.sax

class NetworkReader(xml.sax.ContentHandler):
    def __init__(self, cursor):
        self.cursor = cursor

    def startElement(self, name, attributes):
        if name == 'node':
            id, x, y = attributes['id'], attributes['x'], attributes['y']
            self.cursor.execute('insert into _nodes (id, x, y) values (?,?,?)', (id, x, y))

        elif name == 'link':
            id, from_, to = attributes['id'], attributes['from'], attributes['to']
            self.cursor.execute('insert into _links (id, from_id, to_id) values (?,?,?)', (id, from_, to))

class NetworkReaderTask(util.DatabaseTask):
    def __init__(self, db_path, network_path):
        super().__init__(db_path)
        self.network_path = network_path

    def validate(self):
        return self.check_table_exists('nodes') and self.check_table_exists('links')

    def cleanup(self):
        self.drop_if_exists('nodes')
        self.drop_if_exists('links')

    def perform(self):
        self.cleanup()

        with self.get_connection() as connection:
            connection.execute("""
                create table _nodes (
                    id text,
                    x real,
                    y real)""")

            connection.execute("""
                create table _links (
                    id text,
                    from_id text,
                    to_id text)""")

            reader = NetworkReader(connection.cursor())

            with gzip.open(self.network_path) as f:
                xml.sax.parse(f, reader)

            connection.execute('alter table _nodes rename to nodes')
            connection.execute('alter table _links rename to links')
