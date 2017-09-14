import sys
import os
import subprocess
import shutil
from datetime import datetime
from uuid import uuid4
from string import Template

import non_pseudo
from non_pseudo import config

def write_raspa_file(config, filename, name, helium_void_fraction):
    """Writes RASPA input file for calculating gas loading.

    Args:
        filename (str): path to input file.
        run_id (str): identification string for run.
        material_id (str): name for material.

    Writes RASPA input-file.

    """
    s = Template("""
SimulationType                  MonteCarlo
NumberOfCycles                  $NumberOfCycles
NumberOfInitializationCycles    $NumberOfInitializationCycles
PrintEvery                      10
RestartFile                     no

Forcefield                      GenericMOFs
CutOff                          12.8

Framework                       0
FrameworkName                   $FrameworkName
UnitCells                       2 2 2
HeliumVoidFraction              $HeliumVoidFraction
ExternalTemperature             $ExternalTemperature
ExternalPressure                $ExternalPressure

Component 0 MoleculeName                $MoleculeName
            MoleculeDefinition          TraPPE
            TranslationProbability      1.0
            ReinsertionProbability      1.0
            SwapProbability             1.0
            CreateNumberOfMolecules     0""")
    simulation_config = config['simulations']['gas_adsorption']
    with open(filename, 'w') as raspa_input_file:
        raspa_input_file.write(
                s.substitute(
                    NumberOfCycles = simulation_config['simulation_cycles'],
                    NumberOfInitializationCycles = simulation_config['initialization_cycles'],
                    FrameworkName = name,
                    HeliumVoidFraction = helium_void_fraction,
                    ExternalTemperature = simulation_config['external_temperature'],
                    ExternalPressure = '{} {}'.format(*simulation_config['external_pressure']),
                    MoleculeName = simulation_config['adsorbate']))

def find_output_file(output_dir, pressure):
    if pressure >= 10 ** 6:
        p_string = '{:.1e}'.format(pressure)
    else:
        p_string = str(pressure)

    output_subdir = os.path.join(output_dir, 'Output', 'System_0')
    for file_name in os.listdir(output_subdir):
        if p_string in file_name:
            return os.path.join(output_subdir, file_name)

def parse_output(output_dir, simulation_config):
    """Parse output file for gas loading data.

    Args:
        output_file (str): path to simulation output file.

    Returns:
        results (dict): absolute and excess molar, gravimetric, and volumetric
            gas loadings, as well as energy of average, van der Waals, and
            Coulombic host-host, host-adsorbate, and adsorbate-adsorbate
            interations.

    """
    results = {}
    
    external_pressure = simulation_config['external_pressure']
    if isinstance(external_pressure, list):
        ga0_pressure = max(external_pressure)
        ga1_pressure = min(external_pressure)
    else:
        ga0_pressure = external_pressure
        ga1_pressure = None

    f = 'ga0'
    for p in [ga0_pressure, ga1_pressure]:
        if p != None:
            output_file = find_output_file(output_dir, p)
            with open(output_file) as origin:
                line_counter = 1
                for line in origin:
                    if "absolute [mol/kg" in line:
                        results['{}_absolute_molar_loading'.format(f)] = float(line.split()[5])
                    elif "absolute [cm^3 (STP)/g" in line:
                        results['{}_absolute_gravimetric_loading'.format(f)] = float(line.split()[6])
                    elif "absolute [cm^3 (STP)/c" in line:
                        results['{}_absolute_volumetric_loading'.format(f)] = float(line.split()[6])
                    elif "excess [mol/kg" in line:
                        results['{}_excess_molar_loading'.format(f)] = float(line.split()[5])
                    elif "excess [cm^3 (STP)/g" in line:
                        results['{}_excess_gravimetric_loading'.format(f)] = float(line.split()[6])
                    elif "excess [cm^3 (STP)/c" in line:
                        results['{}_excess_volumetric_loading'.format(f)] = float(line.split()[6])
                    elif "Average Host-Host energy:" in line:
                        host_host_line = line_counter + 8
                    elif "Average Adsorbate-Adsorbate energy:" in line:
                        adsorbate_adsorbate_line = line_counter + 8
                    elif "Average Host-Adsorbate energy:" in line:
                        host_adsorbate_line = line_counter + 8
                    line_counter += 1

            with open(output_file) as origin:
                line_counter = 1
                for line in origin:
                    if line_counter == host_host_line:
                        results['{}_host_host_avg'.format(f)] = float(line.split()[1])
                        results['{}_host_host_vdw'.format(f)] = float(line.split()[5])
                        results['{}_host_host_cou'.format(f)] = float(line.split()[7])
                    elif line_counter == adsorbate_adsorbate_line:
                        results['{}_adsorbate_adsorbate_avg'.format(f)] = float(line.split()[1])
                        results['{}_adsorbate_adsorbate_vdw'.format(f)] = float(line.split()[5])
                        results['{}_adsorbate_adsorbate_cou'.format(f)] = float(line.split()[7])
                    elif line_counter == host_adsorbate_line:
                        results['{}_host_adsorbate_avg'.format(f)] = float(line.split()[1])
                        results['{}_host_adsorbate_vdw'.format(f)] = float(line.split()[5])
                        results['{}_host_adsorbate_cou'.format(f)] = float(line.split()[7])
                    line_counter += 1
        
            f = 'ga1'  # flag for second pressure gas adsorption simulations

            print('Pressure : {}'.format(p))
            print('\n', results, '\n')

    return results

def run(config, run_id, name, helium_void_fraction):
    """Runs gas loading simulation.

    Args:
        run_id (str): identification string for run.
        material_id (str): unique identifier for material.

    Returns:
        results (dict): gas loading simulation results.

    """
    simulation_directory  = config['simulations_directory']

    if simulation_directory == 'non_pseudo':
        non_pseudo_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
        path = os.path.join(non_pseudo_dir, run_id, name)
    elif simulation_directory == 'scratch':
        path = os.environ['LOCAL']
    else:
        print('OUTPUT DIRECTORY NOT FOUND.')
    output_dir = os.path.join(path, 'output_%s_%s' % (name, uuid4()))

    print("Output directory :\t%s" % output_dir)
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, "GasAdsorption.input")

    write_raspa_file(config, filename, name, helium_void_fraction)
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
            print("Calculating gas loading in %s..." % (name))
            print('Running...')
            print(output_dir)
            subprocess.run('simulate GasAdsorption.input', shell=True, check=True, cwd=output_dir)
            print('...done running?')
            results = parse_output(output_dir, config['simulations']['gas_adsorption'])
            shutil.rmtree(path, ignore_errors=True)
            sys.stdout.flush()
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError, KeyError) as err:
            print(err)
            print(err.args)
            continue
        break

    return results
