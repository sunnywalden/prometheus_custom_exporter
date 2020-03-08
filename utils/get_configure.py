#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# from utils.apollo_handler import apo_config
from utils.config import config


def env_file_conf(conf_name, conf_type='string', default=None):

    conf_value = os.getenv(conf_name, default)

    if conf_type == 'int' and conf_value:
        conf_value = int(conf_value)
    if conf_type == 'bool' and conf_value:
        if conf_value.upper() == 'TRUE':
            conf_value = True
        else:
            conf_value = False

    return conf_value


def ini_conf(section, option, default,  file_name=None):

    ini_config = config(filename=file_name)
    conf_value = ini_config.getOption(section=section, option=option, default=default)

    return conf_value

