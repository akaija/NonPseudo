import os

import yaml

import non_pseudo

def load_config_file(file_name):
    """Reads input file.

    Args:
        file_name (str): auto-created config filename (ex. non_pseudo.sample.yaml)
    
    Returns:
        config (dict): parameters specified in config.

    """
    with open(file_name) as config_file:
        config = yaml.load(config_file)
    return config
