#!/bin/bash -l
#SBATCH --job-name=vllm_server
#SBATCH --time=01:00:00
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --constraint=gpu
#SBATCH --gpus-per-node=4
#SBATCH --account=nstaff
#SBATCH --output=vllm_output.log
#SBATCH --image=vllm/vllm-openai:latest
#SBATCH --module=gpu,nccl-plugin

# Parameters
HOSTNAME=$(hostname)
PORT=8000
MODEL=Mistral-7B-Instruct-v0.2
NB_GPUS=4
MODELS_DIR=/global/cfs/cdirs/nstaff/chatbot/models

# Run vLLM from a container
srun shifter --env=OUTLINES_CACHE_DIR=$TMPDIR --image=vllm/vllm-openai \
             python3 -m vllm.entrypoints.openai.api_server \
             --model $MODELS_DIR/$MODEL --host $HOSTNAME --port $PORT --tensor-parallel-size $NB_GPUS
