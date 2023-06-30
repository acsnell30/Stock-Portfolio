import sqlite3
import pandas as pd

def connect_database(database_name):
    connection = sqlite3.connect('data/' + database_name)

    cursor = connection.cursor()

    return connection, cursor


def load_csv(table_name, csv_file, con, cur):
    df = pd.read_csv('data/' + csv_file)

    res = cur.execute("SELECT name FROM sqlite_master").fetchall()
    exists = False
    for tbl in res:
        if table_name == tbl[0]:
            exists = True
            break
    
    if exists == False:
        df.to_sql(table_name, con, if_exists='replace', index=False)