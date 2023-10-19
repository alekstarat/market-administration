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
        self.cur.execute("""CREATE TABLE IF NOT EXISTS TelegramUsers (
            id INT,
            username TEXT, 
            reservationCount INT,
            isBanned INT,
            bannedUntil INT
            )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Reservation (
            operationID INTEGER PRIMARY KEY,
            userID INT,
            positionReserved INT,
            reservationUntil INT
            )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Transactions (
            operationID INT,
            userID INT,
            positionSelled INT,
            timeSelled INT,
            profit INT
        )""")


base = Base('C:/Users/Сашер/Desktop/base.sqlite')
#base.cur.execute("DELETE FROM TelegramUsers")
base.con.commit()
base.con.close()



