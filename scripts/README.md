# Scripts

Large Language Model:

* [`vllm_server.slurm`](./vllm_server.slurm): Starts a single node worker.
* [`large_vllm_server.slurm`](./large_vllm_server.slurm): Starts a multi-node worker, able to handle larger models (this script, inspired by the [Meluxina documentation](https://docs.lxp.lu/howto/llama3-vllm/), relies on `--pipeline-parallel-size` which is [not yet suported by al models](https://docs.vllm.ai/en/stable/serving/distributed_serving.html#details-for-distributed-inference-and-serving)).

Embeddings:

* [`embedding_hf_server.slurm`](./embedding_hf_server.slurm): A lightweight text-embeddings-inference based embedding server (also deals with things like reranking).
* [`embedding_vllm_server.slurm`](./embedding_vllm_server.slurm): A vLLM-based embedding server (supports fewer models, and no built-in query prefixing).

Others:

* [`router_vllm_server.slurm`](./router_vllm_server.slurm): runs both embeddings and a LLM, redirecting requests as needed using a `nginx`-based router (see [`nginx.conf.template`](./nginx.conf.template)).
* [`standalone_vllm_server.slurm`](./standalone_vllm_server.slurm): runs both vLLM and a client script on the same node.
