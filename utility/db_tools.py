"""
@Time: 2022/11/03
@Author: LiuShu
@File: 数据库操作类库
"""
import pymysql
from utility.loggers import logger
from utility.utils import config


class Cur_db(object):
    def __init__(self):
        self.config = config
        self.db_name = self.config['database']['DB']

    def pymysql_cur(self, reback=5):
        """ 连接数据库 """
        try:
            self.conn = pymysql.connect(host=self.config['database']['HOST'], user=self.config['database']['USER'],
                                        password=self.config['database']['PWD'], db=self.db_name,
                                        port=int(self.config['database']['PORT']),
                                        charset='utf8')
        except Exception as e:
            if reback == 0:
                logger.exception('Exception occurred.')
                return
            else:
                logger.exception('Exception occurred.')
                reback -= 1
                return self.pymysql_cur(reback)

    def get_db_name(self):
        """

        :return:
        """
        return self.db_name

    def select(self, sql, params, reback=2):
        """ 查询单条语句，并返回查询所有的结果 """
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            # 单条
            res = cur.fetchone()
            cur.close()
            if res:
                return res
            return
        except Exception as e:
            logger.exception('Exception occurred.')
            if reback > 0:
                reback -= 1
                return self.select(sql, reback)
            else:
                logger.info(str('*' * 100))
                return

    def _select(self, sql, reback=2):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            # 单条
            res = cur.fetchone()
            cur.close()
            if res:
                return res[0]
            return
        except Exception as e:
            logger.exception('Exception occurred.')
            if reback > 0:
                reback -= 1
                return self.select(sql, reback)
            else:
                logger.info(str('*' * 100))
                return

    def selectMany(self, sql, reback=2):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            cur.close()
            if res:
                return res
            logger.info(str(sql))
            return
        except Exception as e:
            logger.exception('Exception occurred.')
            if reback > 0:
                reback -= 1
                return self.selectMany(sql, reback)
            else:
                logger.info(str('*' * 100))
                return

    def insert(self, sql, params):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return

    def _insert(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def insert_batch(self, sql, data_list):
        """
        将dataframe批量入库
        :param sql: 插入语句
        :return:
        """
        cur = self.conn.cursor()
        # 开启事务
        self.conn.begin()
        try:
            cur.executemany(sql, data_list)
            self.conn.commit()
            cur.close()
            self.conn.close()
            return True
        except:
            # 万一失败了，要进行回滚操作
            self.conn.rollback()
            cur.close()
            self.conn.close()
            return False

    def update(self, sql, params):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return

    def _update(self, sql):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            logger.exception('Exception occurred.')

    def close(self):
        self.conn.close()
        pass


if __name__ == '__main__':
    db_con = Cur_db()
    logger.info(str(db_con.config['database']['HOST']))
    print(str(db_con.config['database']['HOST']))
    db_con.pymysql_cur()
    sql = "SELECT * FROM cargo"
    res = db_con.selectMany(sql)
    print(str(res))
    db_con.close()