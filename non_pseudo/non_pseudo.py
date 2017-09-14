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


from collections import Counter

import numpy as np

np_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
cif_dir = os.path.join(np_dir, 'cif_files')

def load_atom_types(name):
    file_path = os.path.join(cif_dir, '{}.cif'.format(name))
#    print('Loading data from : {}'.format(file_path))
    if 'hypothetical' in name:
        atom_types_raw = np.genfromtxt(file_path, usecols=0, skip_header=20, dtype=str)
    else:
        atom_types_raw = np.genfromtxt(file_path, usecols=0, skip_header=24, dtype=str)
    atom_types = []
    for atom_type in atom_types_raw:
        atom_types.append(''.join([i for i in atom_type if not i.isdigit()]))
    return atom_types

def load_LCs(name):
    file_path = os.path.join(cif_dir, '{}.cif'.format(name))
#    print('Loading data from : {}'.format(file_path))
    if 'hypothetical' in name:
        LCs = np.genfromtxt(file_path, usecols=1, skip_header=8, max_rows=3)   
    else:
        LCs = np.genfromtxt(file_path, usecols=1, skip_header=9, max_rows=3)   
    return LCs

def calculate_vol_nden(name):
    file_path = os.path.join(cif_dir, '{}.cif'.format(name))
    if 'hypothetical' in name:
        atom_sites = np.genfromtxt(file_path, usecols=0, skip_header=20, dtype=str)
    else:
        atom_sites = np.genfromtxt(file_path, usecols=0, skip_header=24, dtype=str)
    site_count = len(atom_sites)
    print('Atom-site count : {}'.format(site_count))
    LCs = load_LCs(name)
    v = LCs[0] * LCs[1] * LCs[2]
    return v, site_count / v

def load_LJ_parameters():
    file_path = os.path.join(np_dir, 'non_pseudo', 'simulation', 'forcefield', 'force_field_mixing_rules.def')
#    print('Loading LJ parameters from : {}'.format(file_path))
    atom_types = np.genfromtxt(file_path, usecols=0, skip_header=7, skip_footer=4, dtype=str)
    sigma = np.genfromtxt(file_path, usecols=3, skip_header=7, skip_footer=4)
    epsilon = np.genfromtxt(file_path, usecols=2, skip_header=7, skip_footer=4)
    LJ_parameters = {}
    for i in range(len(atom_types)):
        LJ_parameters[atom_types[i][:-1]] = {}
        LJ_parameters[atom_types[i][:-1]]['sigma'] = sigma[i]
        LJ_parameters[atom_types[i][:-1]]['epsilon'] = epsilon[i]
    return LJ_parameters    

def calculate_average_sigma_epsilon(name):
    atom_types = load_atom_types(name)
    counts = Counter(atom_types)
    
    print(counts)
    
    LJ_parameters = load_LJ_parameters()
    
    print('Chemical species :')
    
    sigma_products, epsilon_products = [], []
    for i in counts:
        print('\t', i)
        count = counts[i]
        
        try:
            sigma = LJ_parameters[i]['sigma']
            sigma_product = count * sigma
            sigma_products.append(sigma_product)
            print('\t\tsigma : {}'.format(sigma))
        except:
            print('Sigma value not found!')
            
        try:
            epsilon = LJ_parameters[i]['epsilon']
            epsilon_product = count * epsilon
            epsilon_products.append(epsilon_product)
            print('\t\tepsilon : {}'.format(epsilon))
        except:
            print('Epsilon value not found!')
            
    return sum(sigma_products) / len(atom_types), sum(epsilon_products) / len(atom_types)

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

def worker_run_loop(run_id):
    """
    Args:
        run_id (str): identification string for run.

    Finds next-to-be-simulated hypothetical or real material and calculates
    properties of interest, saving results to database.
    """
    config = load_config_file(os.path.join(run_id, 'config.yaml'))

    non_pseudo_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
    materials_dir = config['materials_directory']
    mat_dir = os.path.join(non_pseudo_dir, materials_dir)
    mat_names = os.listdir(mat_dir)

    for cif_name in mat_names:
        name = cif_name[:-4]
        add_material_to_database(config, name)
