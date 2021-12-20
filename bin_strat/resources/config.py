import os
import logging as log
import yaml
from os.path import exists


properties = {}
"""
Properties dictionary exported to other packages for use
"""

_application_cfg_fp = './application.yml'
"""
Main Property File for running on the cloud. Contains environment variable references but no secret keys.
File is not gitignored, and exists in the public repository.
"""


_local_cfg_fp = './application-local.yml'
"""
Local Property File for running the app locally. May contain environment variable references, passwords and secret keys. 
File is gitignored, and safe to use locally.
ONLY OVERWRITES PROPERTIES WHICH EXIST IN MAIN APP PROPERTY FILE. (ie adding additional properties is not allowed here)
"""


def interpret_environment_dict(cfg, local = {}):
    """
    Returns a new dict where all references to an environment variable are replaced with the actual value.

    Arguments:
        cfg (dict): the dictionary to interpret.
        local (dict): the local override value, or {} if none.

    Returns:
        dict: a dictionary of indentical size where environment variables replace properties.
    """
    tree = {}
    for key, value in cfg.items():
        if isinstance(value, dict):
            tree[key] = interpret_environment_dict(value, local.get(key, {}))
        elif isinstance(value, list):
            tree[key] = interpret_environment_list(local.get(key, value))
        else:
            tree[key] = interpret_environment_value(value, local.get(key))
    return tree


def interpret_environment_list(cfg):
    """
    Returns a new list where all references to an environment variable are replaced with the actual value.
    Intentionally no override for a list: A list can only be interpreted 'as-is'.

    Arguments:
        cfg (list): the list to interpret.

    Returns:
        list: a list of indentical size where environment variables replace properties.
    """
    tree = []
    for value in cfg:
        if isinstance(value, dict):
            tree.append(interpret_environment_dict(value))
        if isinstance(value, list):
            tree.append(interpret_environment_list(value))
        else:
            tree.append(interpret_environment_value(value))
    return tree


def interpret_environment_value(cfg, local = None):
    """
    Given a key of any type, retrieve environment variable.
    Key must be a string, and must begin with a '$' character.

    Examples:
        - cfg is '$X_MBX_APIKEY' -> replaces property with value of os.getenv("X_MBX_APIKEY")
        - cfg is 'myapikeyvalue' -> not an environment variable reference, value is copied
        - cfg is 0 -> not a string, value is copied

    Arguments:
        cfg (any): the value to interpret
        local (any?): the overriden local property, or None if none.

    Returns:
        any: the intepreted value
    """
    cfg_value = cfg if local is None else local
    if isinstance(cfg_value, str) and cfg_value.startswith('$'):
        return os.getenv(cfg_value[1:], '')
    return cfg_value


def get_property_dict(cfg_fp):
    """
    Opens a property file and parses it into a dictionary. Property file should not be empty or malformed.

    Arguments:
        cfg_fp (str): the filepath of the configuration file

    Returns:
        dict: The YAML property file (as a dictionary)
    """
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

    properties = interpret_environment_dict(master_property_file, local_property_file)
    print(properties)