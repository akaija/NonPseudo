import sys
import os
import subprocess
import shutil
from datetime import datetime
from uuid import uuid4
from string import Template

import non_pseudo
from non_pseudo import config

def write_raspa_file(filename, name):
    """Writes RASPA input file for calculating helium void fraction.

    Args:
        filename (str): path to input file.
        run_id (str): identification string for run.
        material_id (str): name for material.

    Writes RASPA input-file.

    """
    s = Template("""
SimulationType          MonteCarlo
NumberOfCycles          $NumberOfCycles

PrintEvery              10
PrintPropertiesEvery    10

Forcefield              GenericMOFs
CutOff                  12.8

Framework               0
FrameworkName           $FrameworkName
UnitCells               2 2 2
ExternalTemperature     298.0

Component 0 MoleculeName                helium
            MoleculeDefinition          TraPPE
            WidomProbability            1.0
            CreateNumberOfMolecules     0""")
    with open(filename, 'w') as raspa_input_file:
        raspa_input_file.write(
                s.substitute(
                    NumberOfCycles = config['simulations']['helium_void_fraction']['simulation_cycles'],
                    FrameworkName = name))

def parse_output(output_file):
    """Parse output file for void fraction data.

    Args:
        output_file (str): path to simulation output file.

    Returns:
        results (dict): average Widom Rosenbluth-weight.

    """
    results = {}
    with open(output_file) as origin:
        for line in origin:
            if not "Average Widom Rosenbluth-weight:" in line:
                continue
            results['vf_helium_void_fraction'] = float(line.split()[4])
        print("\nVOID FRACTION :   %s\n" % (results['vf_helium_void_fraction']))
    return results

def run(run_id, name):
    """Runs void fraction simulation.

    Args:
        run_id (str): identification string for run.
        material_id (str): unique identifier for material.

    Returns:
        results (dict): void fraction simulation results.

    """
    simulation_directory  = config['simulations_directory']

    if simulation_directory == 'non_pseudo':
        non_pseudo_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
        path = os.path.join(non_pseudo_dir, run_id, name)
    elif simulation_directory == 'scratch':
        path = os.environ['SCRATCH']
    else:
        print('OUTPUT DIRECTORY NOT FOUND.')
    output_dir = os.path.join(path, 'output_%s_%s' % (name, uuid4()))

    print("Output directory :\t%s" % output_dir)
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, "VoidFraction.input")

    write_raspa_file(filename, name)
    force_field_path = os.path.join(non_pseudo_dir, 'non_pseudo', 'simulation', 'forcefield')
    shutil.copy(os.path.join(force_field_path, 'force_field_mixing_rules.def'), output_dir)
    shutil.copy(os.path.join(force_field_path, 'force_field.def'), output_dir)
    shutil.copy(os.path.join(force_field_path, 'pseudo_atoms.def'), output_dir)
    cif_path = os.path.join(non_pseudo_dir, 'cif_files')
    mat_path = os.path.join(cif_path, '%s.cif' % name)
    print(mat_path)
    shutil.copy(mat_path, output_dir)

    while True:
        try:
            print("Date :\t%s" % datetime.now().date().isoformat())
            print("Time :\t%s" % datetime.now().time().isoformat())
            print("Calculating void fraction of %s..." % (name))
            subprocess.run(['simulate', './VoidFraction.input'], check=True, cwd=output_dir)
            filename = "output_%s_2.2.2_298.000000_0.data" % (name)
            output_file = os.path.join(output_dir, 'Output', 'System_0', filename)
            results = parse_output(output_file)
            shutil.rmtree(path, ignore_errors=True)
            sys.stdout.flush()
        except (FileNotFoundError, IndexError, KeyError) as err:
            print(err)
            print(err.args)
            continue
        break

    return results
