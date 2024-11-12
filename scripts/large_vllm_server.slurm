#!/bin/bash -l
#SBATCH --job-name=vllm_server
#SBATCH --time=00:30:00
#SBATCH --qos=debug
#SBATCH --nodes=2
#SBATCH --constraint=gpu
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --account=nstaff
#SBATCH --output=large_vllm_output.log
#SBATCH --image=vllm/vllm-openai:latest
#SBATCH --module=gpu,nccl-2.18

# Ray Parameters
HEAD_HOSTNAME=$(hostname)
HEAD_IPADDRESS=$(hostname --ip-address)
RAY_PORT=8001

# vLLM Parameters
VLLM_PORT=8000
SHIFTER_IMAGE=vllm/vllm-openai
MODELS_DIR=/global/cfs/cdirs/nstaff/chatbot/models
#MODEL=Mistral-7B-Instruct-v0.2
#MODEL=Meta-Llama-3-70B-Instruct
MODEL=c4ai-command-r-plus-08-2024

# Bug fixes
# Needed to get NCCL running properly in multinodes settings
export VLLM_NCCL_SO_PATH="/opt/udiImage/modules/nccl-2.18/lib/libnccl.so.2"
# Needed to avoid having outline try to write to local files
export OUTLINES_CACHE_DIR=$TMPDIR

# Checks if we need a Ray cluster for multi-node deployment
if [ "${SLURM_NNODES}" -gt 1 ]; then
    # Starts Ray head node
    echo "Starting Ray head node"
    srun -J "head ray node-step-%J" -N 1 --ntasks-per-node=1  -c $(( SLURM_CPUS_ON_NODE/2 )) -w ${HEAD_HOSTNAME} \
        shifter --image=$SHIFTER_IMAGE \
        ray start --block --head --port=$RAY_PORT &
    sleep 10

    # Starts Ray worker nodes
    echo "Starting Ray worker node"
    srun -J "worker ray node-step-%J" -N $(( SLURM_NNODES-1 )) --ntasks-per-node=1 -c ${SLURM_CPUS_ON_NODE} -x ${HEAD_HOSTNAME}  \
        shifter --image=$SHIFTER_IMAGE \
        ray start --block --address=${HEAD_IPADDRESS}:${RAY_PORT} &
    sleep 30
else
    echo "Single node detected; skipping Ray setup."
fi

# Run vLLM
echo "Starting vLLM"
shifter --image=$SHIFTER_IMAGE \
        python3 -m vllm.entrypoints.openai.api_server \
        --model $MODELS_DIR/$MODEL --host $HEAD_HOSTNAME --port $VLLM_PORT \
        --tensor-parallel-size $SLURM_GPUS_ON_NODE --pipeline-parallel-size $SLURM_NNODES

# Some Datapoint:
# 1 node will hold a 13b model (more?)
# 2 nodes will hold a 104b model (2 nodes will not)