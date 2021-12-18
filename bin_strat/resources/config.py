import os
import logging as log
import yaml
from os.path import exists

log.root.setLevel(log.INFO)

properties = {}

_local_cfg_fp = './application-local.yml'
_application_cfg_fp = './application.yml'

def interpolate_environment_dict(cfg):
    """
    Returns a new dictionary where environment variable properties are loaded.
    An environment variable property is any value that begins with '$'. (ex: $BINANCE_API_KEY)
    Ignores any values that do not begin with '$', or are not a string.
    Arguments:
        cfg (dict) the dictionary to interpolate.
    Returns:
        dict: a dictionary of indentical size where environment variables replace properties.
    """
    tree = {}
    for key, value in cfg.items():
        if isinstance(value, dict):
            tree[key] = interpolate_environment_dict(value)
        if isinstance(value, list):
            tree[key] = interpolate_environment_list(value)
        else:
            tree[key] = interpolate_environment_value(value)
    return tree

def interpolate_environment_list(cfg):
    tree = []
    for index in range(len(cfg)):
        value = cfg[index]
        if isinstance(value, dict):
            tree[index] = interpolate_environment_dict(value)
        if isinstance(value, list):
            tree[index] = interpolate_environment_list(value)
        else:
            tree[index] = interpolate_environment_value(value)
    return tree

def interpolate_environment_value(cfg):
    if isinstance(cfg, str) and cfg.startswith('$'):
        return os.getenv(cfg[1:], '')
    return cfg

def set_property_export(cfg_fp):
    with open(cfg_fp) as property_file:
        properties_dict: dict = yaml.safe_load(property_file)['properties']
        return interpolate_environment_dict(properties_dict)

if __name__ == '__main__':
    if not exists(_application_cfg_fp):
        raise FileNotFoundError('missing application.yml property file, cannot start application')
    
    properties = set_property_export(_application_cfg_fp)

    if exists(_local_cfg_fp):
        log.info("local configuration file application-local.yml specified, properties will overwrite defaults")
        properties = set_property_export(_local_cfg_fp)
    else:
        log.info("no local configuration file specified, running in production mode")

    print(properties)
