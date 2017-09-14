#!/usr/bin/env python3

from datetime import datetime
import os

import click
import RASPA2
import yaml

import non_pseudo
from non_pseudo.files import load_config_file
from non_pseudo.non_pseudo import worker_run_loop, run_all_simulations, calculate_average_sigma_epsilon, calculate_vol_nden
from non_pseudo.db import Material

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

@nps.command()
@click.argument('run_id')
def launch_worker(run_id):
    """Start process to manage run.

    Args:
        run_id (str): identification string for run.

    Launches worker to identify next material, simulate its properties, and
    store results in database.
    """
    non_pseudo._init(run_id)
    worker_run_loop(run_id)

@nps.command()
@click.argument('crystal_name')
def one_off(crystal_name):
    config = load_config_file(
            os.path.join(
                os.path.dirname(os.path.dirname(non_pseudo.__file__)),
                'settings',
                'non_pseudo.yaml'))
    crystal = Material(crystal_name)
    crystal.run_id = 'one_off'

    print('SCREENING : {}'.format(crystal_name))

    run_all_simulations(config, crystal)
    print('...done!\n')

    print('Crystal name :\t\t{}'.format(crystal_name))
    print('CH4 v/v 35bar :\t\t{}'.format(crystal.ga1_absolute_volumetric_loading))
    print('CH4 v/v 65bar :\t\t{}'.format(crystal.ga0_absolute_volumetric_loading))
    print('He void fraction :\t{}'.format(crystal.vf_helium_void_fraction))
    print('Vol. surface area :\t{}\n'.format(crystal.sa_volumetric_surface_area))

    avg_sig, avg_ep = calculate_average_sigma_epsilon(crystal_name)
    v, nd = calculate_vol_nden(crystal_name)

    print('\nAvg. sigma-value :\t{}'.format(avg_sig))
    print('Avg. epsilon-value :\t{}'.format(avg_ep))
    print('Unit cell vol. :\t{}'.format(v))
    print('Number density :\t{}'.format(nd))

if __name__ == '__main__':
    nps()
