import sqlite3

conn = sqlite3.connect('store.db')
cursor = conn.cursor()

def sql_execute(sql, vals=[]):
    cursor.execute(sql, vals)
    return cursor.fetchall()
