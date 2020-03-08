#!env/bin/python
# -*- coding:utf-8 -*-
# author: sunnywalden@gmail.com

import requests
import json

from utils.get_configure import env_file_conf
from utils.apollo_handler import ApolloQuery


def prometh_hosts():
    """
            从apollo查询prome地址
            :return: list
    """
    external = env_file_conf('EXTERNAL', conf_type='bool')
    if not external:
        conf_name = 'prome_host'
    else:
        conf_name = 'prome_external_host'
    if external:
        print('Conneting to apollo from external net!')
    apollo_query = ApolloQuery()
    prome_hosts = None
    try:
        prome_hosts = apollo_query.apo_config(conf_name).split(',')
    except Exception as e:
        print('Getting prometheus addr from apollo failed!{}'.format(e.__str__()))
        exit(1)

    print('Debug prometheus hosts: {}'.format(prome_hosts))

    return prome_hosts


def prome_query(prome_sql):
    """
            查询prome
            :param prome_sql: promesql
            :return:
    """
    res = None
    res_data = None

    prome_host = prometh_hosts()
    time_out = 60 * 3

    if not prome_host: exit(1)
    try:
        res = requests.request(method="get", url='http://' + prome_host[0] + prome_sql, timeout=time_out)
    except requests.RequestException as e:
        try:
            res = requests.request(method="get", url='http://' + prome_host[1] + prome_sql, timeout=time_out)
        except Exception as e1:
            print("Query prometheus failed!{}".format(e1.__str__()))
            exit(1)
    except TypeError as e:
        print("Gettting prometheus addr from apollo failed!{}".format(e.__str__()))

    print('Prometheus returned: {} {}'.format(res.status_code, res.raw))

    if 400 <= res.status_code < 600:
        print('Error query prome {} {}'.format(res.status_code, res.content))
        exit(1)
    else:
        try:
            res_content = json.loads(res.content)
            print("prome returned:{} {}".format(res.status_code, res_content))
        except Exception as e:
            res_content = res.content

        res_status = res_content["status"]
        res_data = res_content["data"]
        if not res_status == "success":
            print("prome returned:{} {}".format(res.status_code, res_status))
            exit(1)

    return res_data
