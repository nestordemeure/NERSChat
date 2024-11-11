# Scripts

* [`vllm_server.slurm`](./vllm_server.slurm): Starts a single node worker.
* [`debug_vllm_server.slurm`](./debug_vllm_server.slurm): Same as `vllm_server.slurm` but shorter-lived adn faster starting.
* [`large_vllm_server.slurm`](./large_vllm_server.slurm): Starts a multi-node worker, able to handle larger models (this script, inspired by the [Meluxina documentation](https://docs.lxp.lu/howto/llama3-vllm/), relies on `--pipeline-parallel-size` which is [not yet suported by al models](https://docs.vllm.ai/en/stable/serving/distributed_serving.html#details-for-distributed-inference-and-serving)).
