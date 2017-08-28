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
    """Writes RASPA input file for calculating surface area.

    Args:
        filename (str): path to input file.
        run_id (str): identification string for run.
        material_id (str): name for material.

    Writes RASPA input-file.

    """
    s = Template("""
SimulationType          MonteCarlo
NumberOfCycles          $NumberOfCycles

PrintEvery              1
PrintPropertiesEvery    1

Forcefield              GenericMOFs
CutOff                  12.8

Framework               0
FrameworkName           $FrameworkName
UnitCells               2 2 2
SurfaceProbeDistance    Sigma

Component 0 MoleculeName                N2
            StartingBead                0
            MoleculeDefinition          TraPPE
            SurfaceAreaProbability            1.0
            CreateNumberOfMolecules     0""")
    with open(filename, 'w') as raspa_input_file:
        raspa_input_file.write(
                s.substitute(
                    NumberOfCycles = config['simulations']['surface_area']['simulation_cycles'],
                    FrameworkName = name))

def parse_output(output_file):
    """Parse output file for surface area data.

    Args:
        output_file (str): path to simulation output file.

    Returns:
        results (dict): total unit cell, gravimetric, and volumetric surface
            areas.

    """
    results = {}
    with open(output_file) as origin:
        count = 0
        for line in origin:
            if "Surface area" in line:
                if count == 0:
                    results['sa_unit_cell_surface_area'] = float(line.split()[2])
                    count = count + 1
                elif count == 1:
                    results['sa_gravimetric_surface_area'] = float(line.split()[2])
                    count = count + 1
                elif count == 2:
                    results['sa_volumetric_surface_area'] = float(line.split()[2])

    print(
        "\nSURFACE AREA\n" +
        "%s\tA^2\n"      % (results['sa_unit_cell_surface_area']) +
        "%s\tm^2/g\n"    % (results['sa_gravimetric_surface_area']) +
        "%s\tm^2/cm^3"   % (results['sa_volumetric_surface_area']))
    return results

def run(run_id, name):
    """Runs surface area simulation.

    Args:
        run_id (str): identification string for run.
        material_id (str): unique identifier for material.

    Returns:
        results (dict): surface area simulation results.

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
    filename = os.path.join(output_dir, "SurfaceArea.input")

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
            print("Calculating surface area of %s..." % (name))
            subprocess.run(['simulate', './SurfaceArea.input'], check=True, cwd=output_dir)
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
