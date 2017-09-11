#!/bin/bash
#
# $Revision: 1.0 $
# $Date:  2017-09-11 $
# $Author: akaija $

#SBATCH -N 1
#SBATCH -t 1-12:00 # Runtime in D-HH:MM
#SBATCH --cpus-per-task=16
#SBATCH --mem=2g

echo JOB_ID: $SLURM_JOB_ID JOB_NAME: $SLURM_JOB_NAME HOSTNAME: $SLURM_SUBMIT_HOST
echo start_time: `date`

# dependencies
module purge
module load python/3.5.1
module load postgresql/9.5.2

source ~/venv/htsohm/bin/activate

cd $SLURM_SUBMIT_DIR
sjs_launch_workers.sh $SLURM_CPUS_ON_NODE $stay_alive

# workaround for .out / .err files not always being copied back to $PBS_O_WORKDIR
cp /var/spool/torque/spool/$SLURM_JOB_ID.OU $SLURM_SUBMIT_DIR/$SLURM_JOB_ID$(hostname)_$$.out
cp /var/spool/torque/spool/$SLURM_JOB_ID.ER $SLURM_SUBMIT_DIR/$SLURM_JOB_ID$(hostname)_$$.err

exit
