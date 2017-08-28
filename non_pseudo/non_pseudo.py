import os
import sys

import non_pseudo
from non_pseudo import config
from non_pseudo.db import session, Material
from non_pseudo import simulation

def run_all_simulations(material):
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
        results = simulation.helium_void_fraction.run(material.run_id, material.name)
        material.update_from_dict(results)

    # gas loading simulation
    if 'gas_adsorption' in simulations:
        results = simulation.gas_adsorption.run(material.run_id, material.name, material.vf_helium_void_fraction)
        material.update_from_dict(results)

    if 'surface_area' in simulations:
        results = simulation.surface_area.run(material.run_id, material.name)
        material.update_from_dict(results)

def worker_run_loop(run_id):
    """
    Args:
        run_id (str): identification string for run.

    Finds next-to-be-simulated hypothetical or real material and calculates
    properties of interest, saving results to database.
    """
    non_pseudo_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
    materials_dir = config['materials_directory']
    mat_dir = os.path.join(non_pseudo_dir, materials_dir)
    mat_names = os.listdir(mat_dir)

    for cif_name in mat_names:
        name = cif_name[:-4]

        material = Material(name)
        material.name = name
        material.run_id = run_id

        session.add(material)
        run_all_simulations(material)
        session.commit()
