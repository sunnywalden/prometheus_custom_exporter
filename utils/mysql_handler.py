#!/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

import pymysql

from utils.apollo_handler import ApolloQuery
from utils.get_configure import env_file_conf


def mysql_conn(db_host, db_port, database, db_user, db_passwd):
    # 打开数据库连接
    try:
        conn = pymysql.Connect(
            host=db_host, port=db_port, user=db_user, passwd=db_passwd, db=database, charset='utf8', connect_timeout=60
        )

    except pymysql.err.OperationalError as e:
        print('Connect to Mysql host {}:{} failed!{}'.format(db_host, db_port, e.__str__()))
        exit(1)
    else:
        return conn


def mysql_excute(conn, sql):
    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()

    # SQL 插入语句
    # sql = "INSERT INTO %s \
    #        VALUES ('%s', '%s',  %s,  '%s',  %s)" % \
    #       (database, product, env_type, service, datetime, ava)
    try:
        # 执行sql语句
        cursor.execute(sql)
    # 执行sql语句
        conn.commit()
    except:
        # 发生错误时回滚
        conn.rollback()

    # 关闭数据库连接
    # conn.close()
