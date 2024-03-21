import sqlite3

class CameraDB:
    def __init__(self, db_name='cameras.db'):
        self.db_name = db_name
        self.conn = None
        self.create_table()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)

    def create_table(self):
        self.connect()
        query = '''CREATE TABLE IF NOT EXISTS cameras
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     location TEXT NOT NULL)'''
        self.conn.execute(query)
        self.conn.commit()

    def add_camera(self, name, location):
        self.connect()
        query = 'INSERT INTO cameras (name, location) VALUES (?, ?)'
        self.conn.execute(query, (name, location))
        self.conn.commit()

    def get_cameras(self):
        self.connect()
        query = 'SELECT * FROM cameras'
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def update_camera(self, camera_id, name=None, location=None):
        self.connect()
        query = 'UPDATE cameras SET name = ?, location = ? WHERE id = ?'
        self.conn.execute(query, (name, location, camera_id))
        self.conn.commit()

    def remove_camera(self, camera_id):
        self.connect()
        query = 'DELETE FROM cameras WHERE id = ?'
        self.conn.execute(query, (camera_id,))
        self.conn.commit()

    def __del__(self):
        if self.conn:
            self.conn.close()

