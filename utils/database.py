import mysql.connector


class DataBase:

    def __init__(self, **kwargs):
        self.pool = mysql.connector.connect(**kwargs)

    def cursor(self):
        return self.pool.cursor()
