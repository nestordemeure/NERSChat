#!/bin/bash -l
#SBATCH --job-name=router_vllm_server
#SBATCH --time=00:30:00
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --constraint=gpu
#SBATCH --exclusive
#SBATCH --account=nstaff
#SBATCH --output=router_output.log
#SBATCH --image=vllm/vllm-openai:latest
#SBATCH --module=gpu,nccl-plugin
#SBATCH --volume="/global/cfs/cdirs/nstaff/chatbot/models:/data"

# General Parameters
export HOSTNAME=$(hostname -i)
export PORT=8000
MODELS_DIR=/global/cfs/cdirs/nstaff/chatbot/models

# Embedder Parameters
export HOSTNAME_EMBEDDINGS=$HOSTNAME
export PORT_EMBEDDINGS=8001
MODEL_EMBEDDINGS=bge-large-en-v1.5
IMAGE_EMBEDDINGS=ghcr.io/huggingface/text-embeddings-inference:latest

# LLM Parameters
export HOSTNAME_LLM=$HOSTNAME
export PORT_LLM=8002
MODEL_LLM=Mistral-7B-Instruct-v0.2
IMAGE_LLM=vllm/vllm-openai:latest

# router Parameters
IMAGE_ROUTER=nginx:latest
CONFIGURATION_ROUTER=nginx.conf.template

# Run embedder container
echo "Starting embedder"
srun --overlap --ntasks-per-node=1 --gpus-per-task=1 --gpu-bind=map_gpu:0  \
     shifter --image=$IMAGE_EMBEDDINGS text-embeddings-router \
     --model-id $MODELS_DIR/$MODEL_EMBEDDINGS --hostname $HOSTNAME_EMBEDDINGS --port $PORT_EMBEDDINGS &

# Run LLM container
# Overlap on GPU0, it is that or using 2 gpus (we need the number of gpus to be even so 3 would not do).
echo "Starting LLM"
srun --overlap --ntasks-per-node=1 --gpus-per-task=4 \
     shifter --env=OUTLINES_CACHE_DIR=$TMPDIR --image=$IMAGE_LLM \
     python3 -m vllm.entrypoints.openai.api_server \
     --model $MODELS_DIR/$MODEL_LLM --host $HOSTNAME_LLM --port $PORT_LLM --tensor-parallel-size 4 &

# Create a router config file
echo "Generating router config file"
envsubst '${TMPDIR} ${PORT} ${HOSTNAME_EMBEDDINGS} ${PORT_EMBEDDINGS} ${HOSTNAME_LLM} ${PORT_LLM}' < "${CONFIGURATION_ROUTER}" > "${PWD}/nginx.conf"

# Run router
echo "Starting router"
shifter --image=$IMAGE_ROUTER nginx -c "${PWD}/nginx.conf"

# Wait for everything to conclude
wait
