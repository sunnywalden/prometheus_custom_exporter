#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from pyapollo import ApolloClient

from utils.get_configure import ini_conf, env_file_conf


def apo_client(section, file_name):
    """
            获取apollo连接
            :return: ApolloClient
    """
    apollo_host = ini_conf(section=section, option='host', default='127.0.0.1', file_name=file_name)
    apollo_port = ini_conf(section=section, option='port', default=8080, file_name=file_name)
    apollo_cluster = ini_conf(section=section, option='cluster', default='default', file_name=file_name)
    apollo_app_id = ini_conf(section=section, option="app_id", default="", file_name=file_name)

    print("Debug apollo configure: {} {} {} {}".format(apollo_host, apollo_port, apollo_cluster, apollo_app_id))

    ap_client = ApolloClient(
        app_id=apollo_app_id,
        config_server_url='http://' + apollo_host + ':' + str(apollo_port),
        cluster=apollo_cluster,
        timeout=300
    )

    ap_client.start()

    return ap_client


class ApolloQuery(object):

    def __init__(self):

        self.file_name = 'configs/apollo.ini'
        self.env_type = env_file_conf('ENV_TYPE').upper() if env_file_conf('ENV_TYPE') else "DEV"
        self.client = apo_client(self.env_type, self.file_name)

        self.client.start()

    def __del__(self):
        self.client.stop()

    def apo_config(self, conf_name=None, conf_type=None, default_val=None):
        """
                查询服务可用性
                :param conf_name: 配置项名称
                :param conf_type: 配置项类型
                :param default_val: 默认值
                :return: string or int or bool
        """
        namespace = ini_conf(
            section=self.env_type, option="namespace", default="application", file_name=self.file_name
        )
        conf_value = self.client.get_value(conf_name, default_val=default_val, namespace=namespace)
        if conf_type == 'int' and conf_value:
            conf_value = int(conf_value)
        if conf_type == 'bool' and conf_value:
            if conf_value.upper() == 'TRUE':
                conf_value = True
            else:
                conf_value = False

        return conf_value

