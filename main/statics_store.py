#!env/bin/python
# -*- coding:utf-8 -*-
# author: sunnywalden@gmail.com

import schedule
import time
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "."))
sys.path.append(BASE_DIR)

from utils.mysql_handler import mysql_conn,mysql_excute
from utils.get_configure import env_file_conf
from utils.apollo_handler import ApolloQuery
from main.service_healthcheck import ServiceHealth


def static_storage(static_interval):
    """
            查询服务可用性
            :param product: 产品名称
            :param service: 服务名称
            :param env_type: 环境类型
            :return: float
    """
    env_type = env_file_conf('ENV_TYPE').upper() if env_file_conf('ENV_TYPE') else "DEV"
    external = env_file_conf('EXTERNAL')

    apollo_query = ApolloQuery()
    host_conf_name = 'mysql_host'
    if external.upper() != "FALSE":
        host_conf_name = 'mysql_external_host'

    db_host = apollo_query.apo_config(host_conf_name)
    db_port = apollo_query.apo_config('mysql_port')
    database = apollo_query.apo_config('mysql_db')
    table = apollo_query.apo_config('mysql_table')
    db_user = apollo_query.apo_config('mysql_user')
    db_passwd = apollo_query.apo_config('mysql_passwd')

    service_dict = {}
    service_health = ServiceHealth()
    all_product = service_health.query_product()

    conn = mysql_conn(db_host, db_port, database, db_user, db_passwd)

    for product in all_product:
        service_dict[product] = service_health.query_service(product=product)

    for product, service_list in service_dict.items():
        for service in service_list:
            service_ava = service_health.service_availability(product, service, static_interval)

            print(
                'Debug service {} of product {} availability of environment{}: {} '.format(
                    product, env_type, service, env_type,
                    service_ava))

            sql = service_health.sql_genarate(table, product, service, float('%.4f' % service_ava))
            mysql_excute(conn, sql)

    conn.close()


def schedule_statics():
    """
            查询服务可用性
            :param product: 产品名称
            :param service: 服务名称
            :param env_type: 环境类型
            :return: float
    """

    schedule.every().day.at("00:05").do(static_storage(static_interval='day'))
    schedule.every().week.do(static_storage(static_interval='week'))
    while True:
        schedule.run_pending()
        time.sleep(60 * 60)
