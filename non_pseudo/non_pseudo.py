import os
import sys
from datetime import datetime

import RASPA2
import yaml

import non_pseudo
from non_pseudo import config
from non_pseudo.db import session, Material
from non_pseudo.files import load_config_file
from non_pseudo import simulation

def run_all_simulations(config, material):
    """Simulate gas loading, surface area, and/or void fraction.

    Args:
        Material (sqlalchemy.orm.Query): material to be analyzed.

    Depending on properties specified in config, add simulated data for gas
    loading (including heat of adsorption), surface area, and/or void fraction
    data to record for a particular material within database.

    """
    simulations = config['simulations']

    # void fraction simulation
    if 'helium_void_fraction' in simulations:
        results = simulation.helium_void_fraction.run(config, material.run_id, material.name)
        material.update_from_dict(results)

    # gas loading simulation
    if 'gas_adsorption' in simulations:
        results = simulation.gas_adsorption.run(config, material.run_id, material.name, material.vf_helium_void_fraction)
        material.update_from_dict(results)

    if 'surface_area' in simulations:
        results = simulation.surface_area.run(config, material.run_id, material.name)
        material.update_from_dict(results)

def add_material_to_database(config, name):
    material = Material(name)
    material.run_id = config['run_id']
    session.add(material)
    run_all_simulations(config, material)
    session.commit()

def start_run(config_path):
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

    return config

def worker_run_loop(config_path):
    """
    Args:
        run_id (str): identification string for run.

    Finds next-to-be-simulated hypothetical or real material and calculates
    properties of interest, saving results to database.
    """
    config = start_run(config_path)

    non_pseudo_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
    materials_dir = config['materials_directory']
    mat_dir = os.path.join(non_pseudo_dir, materials_dir)
    mat_names = os.listdir(mat_dir)

    for cif_name in mat_names:
        name = cif_name[:-4]
        add_material_to_database(config, name)
