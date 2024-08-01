from sqlite3 import Cursor
con=sqlite3.content("kütüphane.db")
Cursor=con.cursor()


class kütüphane():
    def __init__(self):
        self.bağlantı()
    
    def bağlantı(self):
        self.bağlantı=sqlite3.connect("kütüphane.db")
        self.cursor=self.bağlantı.cursor()
