#!/usr/bin/env python3
import sys
import os

import sjs

import non_pseudo
from non_pseudo.non_pseudo import start_run, add_material_to_database

config_path = sys.argv[1]

config = start_run(config_path)
run_id = config['run_id']

sjs.load(os.path.join('settings', 'sjs.yaml'))
job_queue = sjs.get_job_queue()

if job_queue is not None:
    print('Queueing jobs onto queue :\t{}'.format(job_queue))
    np_dir = os.path.dirname(os.path.dirname(non_pseudo.__file__))
    materials_dir = config['materials_directory']
    mat_dir = os.path.join(np_dir, materials_dir)
    mat_names = [e[:-4] for e in os.listdir(mat_dir)]

    output_dir = os.path.join(np_dir, run_id)
    for name in mat_names:
        print(name)
        job_queue.enqueue(add_material_to_database, config, name)
