#!/bin/bash -l
#SBATCH --job-name=embedding_vllm_server
#SBATCH --time=00:30:00
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --constraint=gpu
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --account=nstaff
#SBATCH --output=embedding_vllm_output.log
#SBATCH --image=vllm/vllm-openai:latest
#SBATCH --module=gpu,nccl-plugin

# Parameters
HOSTNAME=$(hostname)
PORT=8000
#MODEL=all-mpnet-base-v2 # non-supported MPNetForMaskedLM architecture
#MODEL=bge-large-en-v1.5 # non-supported Bertbase architecture
MODEL=e5-mistral-7b-instruct
MODELS_DIR=/global/cfs/cdirs/nstaff/chatbot/models
SHIFTER_IMAGE=vllm/vllm-openai

# Run vLLM from a container
srun shifter --env=OUTLINES_CACHE_DIR=$TMPDIR --image=$SHIFTER_IMAGE \
             python3 -m vllm.entrypoints.openai.api_server \
             --model $MODELS_DIR/$MODEL --host $HOSTNAME --port $PORT --tensor-parallel-size $SLURM_GPUS_ON_NODE
