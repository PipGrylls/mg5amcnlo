#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --mem-per-cpu=3700
#SBATCH --time=01:00:00
#SBATCH --partition=devel

module purge
module load GCC/10.2.0 OpenMPI/4.0.5 CUDA/11.1.1
module load GCCcore/10.2.0
module load Python/3.8.6
module load dask/2021.2.0

srun /home/epp/phskjp/MCgen/PipGrylls_mg5amcnlo/bin/mg5_aMC /home/epp/phskjp/MCgen/PipGrylls_mg5amcnlo/test_ssWWjj_QCD/test_ssWWjj_QCD.mg
