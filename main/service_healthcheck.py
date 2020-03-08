#!env/bin/python
# -*- coding:utf-8 -*-
# author: sunnywalden@gmail.com

import os
import sys
import datetime

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "."))
sys.path.append(BASE_DIR)

from utils.apollo_handler import ApolloQuery
from utils.prome_query import prome_query
from utils.mysql_handler import mysql_excute, mysql_conn
from utils.get_configure import env_file_conf


class ServiceHealth(object):
    def __init__(self):
        self.api = '/api/v1/query?query='
        apollo_query = ApolloQuery()
        self.prome_host = apollo_query.apo_config("prome_host")
        self.prome_sql = apollo_query.apo_config("prome_query")

    def query_product(self):
        """
                查询所有产品线
                :return: list
        """

        query_sql = '/api/v1/label/product/values'
        products_list = prome_query(query_sql)

        print('All products we have:{}'.format(','.join(products_list)))

        return products_list

    def query_env(self):
        """
                查询所有产品线
                :return: list
        """

        env_type = env_file_conf('ENV_TYPE').upper() if env_file_conf('ENV_TYPE') else "DEV"

        return env_type

    def query_service(self, product=None):
        """
        查询产品线所有服务
        :param product: 产品名称
        :return: list
        """

        query_sql = '/api/v1/label/service/values'
        services_list = prome_query(query_sql)

        sop_pre = 'PLATFORM-'
        vms_pre = 'itl-'

        if product.upper() == 'SOP':
            service_name_pre = sop_pre

        if product.upper() == 'VMS':
            service_name_pre = vms_pre
        else:
            service_name_pre = ''
        if product:
            services = list(filter(
                lambda service: service.startswith(service_name_pre), services_list
            ))
        else:
            services = list(filter(
                lambda service: not service.startswith(sop_pre) and not service.startswith(vms_pre), services_list
            ))
        print('Service of product {}:{}'.format(product, ','.join(services)))

        return services

    def service_availability(self, service, product=None, env_type='prod', static_interval='day'):
        """
                查询服务可用性
                :param product: 产品名称
                :param service: 服务名称
                :param env_type: 环境类型
                :return: float
        """
        if static_interval == 'day':
            time_interval = '24h'
            time_offset = '1h'
        elif static_interval == 'week':
            time_interval = '7d'
            time_offset = '1d'
        else:
            time_interval = '30d'
            time_offset = '1d'
        query_sql = self.api + 'avg(avg_over_time(service_health_status{env_type=~"' + \
                    env_type + \
                    '",product=~"' + product + \
                    '",service=~"' + service + \
                    '"} [' + \
                    time_interval + '] offset ' + time_offset + '))'

        service_ava = prome_query(query_sql)

        print("Service {} of product {} in env {} avalibility:{}".format(service, product, env_type, service_ava))

        return service_ava

    def sql_genarate(self, table, product, service, ava):
        env_type = self.query_env()
        yesterday = datetime.date.today() + datetime.timedelta(-1)
        sql = 'INSERT INTO %s values(%s, %s, %s, %s, %s)' % \
              (table, product, env_type, service, yesterday, ava)

        return sql


if __name__ == '__main__':

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
            service_ava = service_health.service_availability(product, service)

            print(
                'Debug service {} of product {} availability of environment{}: {} '.format(
                    product, env_type, service, env_type,
                    service_ava))

            sql = service_health.sql_genarate(table, product, service, float('%.4f' % service_ava))
            mysql_excute(conn, sql)

    conn.close()
