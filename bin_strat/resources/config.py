import os
import logging as log
import yaml
from os.path import exists


properties = {}


_application_cfg_fp = './application.yml'
"""
Main Property File for running on the cloud. Contains environment variable references but no secret keys.
File is not gitignored, and exists in the public repository.
"""


_local_cfg_fp = './application-local.yml'
"""
Local Property File for running the app locally. May contain environment variable references, passwords and secret keys. 
File is gitignored, and safe to use locally.
"""


def interpolate_environment_dict(cfg, local):
    """
    Returns a new dict where all references to an environment variable are replaced with the actual value.
    Arguments:
        cfg (dict) the dictionary to interpolate.
    Returns:
        dict: a dictionary of indentical size where environment variables replace properties.
    """
    tree = {}
    for key, value in cfg.items():
        local_override = None
        if local is not None:
            local_override = local.get(key)
        if isinstance(value, dict):
            tree[key] = interpolate_environment_dict(value, local_override)
        elif isinstance(value, list):
            tree[key] = interpolate_environment_list(value if local_override is None else local_override)
        else:
            tree[key] = interpolate_environment_value(value, local_override)
    return tree


def interpolate_environment_list(cfg):
    """
    Returns a new list where all references to an environment variable are replaced with the actual value.
    Arguments:
        cfg (list) the list to interpolate.
    Returns:
        list: a list of indentical size where environment variables replace properties.
    """
    tree = []
    for index in range(len(cfg)):
        value = cfg[index]
        if isinstance(value, dict):
            tree.append(interpolate_environment_dict(value))
        if isinstance(value, list):
            tree.append(interpolate_environment_list(value))
        else:
            tree.append(interpolate_environment_value(value))
    return tree


def interpolate_environment_value(cfg, local = None):
    """
    Given a key of any type, retrieve environment variable.
    Key must be a string, and must begin with a '$' character.

    Examples:
        - cfg is '$X_MBX_APIKEY' -> replaces property with value of os.getenv("X_MBX_APIKEY")
        - cfg is 'myapikeyvalue' -> not an environment variable reference, value is copied
        - cfg is 0 -> not a string, value is copied
    Arguments:
        cfg (any): the value to retrieve or ignore
    Returns:
        any: the value either converted or ignored
    """
    if local is not None:
        return local
    if isinstance(cfg, str) and cfg.startswith('$'):
        return os.getenv(cfg[1:], '')
    return cfg


def get_property_dict(cfg_fp):
    with open(cfg_fp) as property_file:
        property_dict: dict = yaml.safe_load(property_file)
        if property_dict is None:
            raise ValueError('file \'%s\' exists, but has no properties or is malformed' % cfg_fp)
        return property_dict


if __name__ == '__main__':
    if not exists(_application_cfg_fp):
        raise FileNotFoundError('missing application.yml property file, cannot start application')
    
    master_property_file = get_property_dict(_application_cfg_fp)

    local_property_file = None
    if exists(_local_cfg_fp):
        log.info("local configuration file application-local.yml specified, properties will overwrite defaults")
        local_property_file = get_property_dict(_local_cfg_fp)
    else:
        log.info("no local configuration file specified, running in production mode")

    properties = interpolate_environment_dict(master_property_file, local_property_file)
    print(properties)
