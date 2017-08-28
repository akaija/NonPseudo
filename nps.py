#!/usr/bin/env python3

from datetime import datetime
import os

import click
import RASPA2
import yaml

import non_pseudo
from non_pseudo.files import load_config_file

@click.group()
def nps():
    pass

@nps.command()
@click.argument('config_path', type=click.Path())
def start(config_path):
    """Create new run.

    Args:
        config_path (str): path to config file (ex: settings/non_pseudo.sample.yaml)

    Prints run_id, creates run-directory with config-file.

    """
    config = load_config_file(config_path)
    non_pseudo_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
    run_id = datetime.now().isoformat()
    config['run_id'] = run_id
    config['raspa2_dir'] = os.path.dirname(RASPA2.__file__)
    config['non_pseudo_dir'] = non_pseudo_dir

    run_dir = os.path.join(non_pseudo_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)
    file_name = os.path.join(run_dir, 'config.yaml')
    with open(file_name, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)
    print('Run created with id: {}'.format(run_id))

if __name__ == '__main__':
    nps()
