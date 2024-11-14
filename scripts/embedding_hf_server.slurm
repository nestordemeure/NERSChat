#!/bin/bash -l
#SBATCH --job-name=embedding_vllm_server
#SBATCH --time=00:30:00
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --constraint=gpu
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --account=nstaff
#SBATCH --output=embedding_hf_output.log
#SBATCH --image=ghcr.io/huggingface/text-embeddings-inference:latest
#SBATCH --module=gpu,nccl-plugin
#SBATCH --volume="/global/cfs/cdirs/nstaff/chatbot/models:/data"

# Parameters
HOSTNAME=$(hostname)
PORT=8000
MODEL=bge-large-en-v1.5
MODELS_DIR=/global/cfs/cdirs/nstaff/chatbot/models
SHIFTER_IMAGE=ghcr.io/huggingface/text-embeddings-inference:latest

# To set a default message type (such as queries):
# --default-prompt-name
# --default-prompt
# (this can be overloaded when using their API)

# Run text-embeddings-inference from a container
srun shifter --image=$SHIFTER_IMAGE \
             text-embeddings-router \
             --model-id $MODELS_DIR/$MODEL --hostname $HOSTNAME --port $PORT
