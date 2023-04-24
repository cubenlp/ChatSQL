# Author: Liushu
# Date: 2023-04-24
# 这里的只是用来校验生成SQL的正确性
import sqlite3

class db_operate(object):
    
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def create_table(self, table_name, table_schema):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {table_schema}")
        self.conn.commit()
    
    def insert_data(self, table_name, data):
        self.cursor.execute(f"INSERT INTO {table_name} VALUES {data}")
        self.conn.commit()
    
    def update_data(self, table_name, data, condition):
        self.cursor.execute(f"UPDATE {table_name} SET {data} WHERE {condition}")
        self.conn.commit()
    
    def delete_data(self, table_name, condition): 
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
        self.conn.commit()
    
    def query_data(self, SQL_statement):
        self.cursor.execute(SQL_statement)
        return self.cursor.fetchall()
