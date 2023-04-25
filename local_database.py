# Author: Liushu
# Date: 2023-04-24
# 这里的只是用来校验生成SQL的正确性
import sqlite3
import numpy as np
from utility.utils import config_dict as DB_CONFIG


class db_operate(object):
    
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def create_table(self, SQL):
        self.cursor.execute(SQL)
        self.conn.commit()

    def insert_data(self, SQL, data):
        self.cursor.executemany(SQL, data)
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


if __name__ == "__main__":
    db_path = DB_CONFIG["db_path"]
    TABLE = DB_CONFIG["TABLE"]
    dboperate = db_operate(db_path)
    print("建表中...")
    # 建表
    for table_name in TABLE.keys():
        table_field_sql = f"create table if not exists {table_name} ("
        for idx, filed in enumerate(TABLE[table_name]["field"].items()):
            if idx == len(TABLE[table_name]["field"].items()) - 1:
                table_field_sql += filed[0] + f" {filed[1][1]})"
            else:
                table_field_sql += filed[0] + f" {filed[1][1]},"
        # 建表语句
        dboperate.create_table(table_field_sql)
    
    print("插入数据中...")
    # 插入数据
    TABLE_Values = DB_CONFIG["TABLE_Values"]
    for table_name in TABLE.keys():
        table_field_sql = f"INSERT INTO {table_name} VALUES ("
        field_len = len(list(TABLE_Values[table_name]["field"].keys()))
        insert_slot = ",".join(['?' for i in range(field_len)])
        table_field_sql += insert_slot + ")"
        table_val = np.array(list(TABLE_Values[table_name]["field"].values())).T.tolist() # 转置+list
        dboperate.insert_data(table_field_sql, table_val)