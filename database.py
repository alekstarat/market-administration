import sqlite3


class Base:

    def __init__(self, path):
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Liquids (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            price INT,
            amount INT
            )""")





base = Base('base.sqlite')

base.con.close()



