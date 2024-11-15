# NERSChat: A SLURM-based Chatbot Worker

This code lets you deploy a [container-based vLLM server](https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html) on a SLURM cluster (specifically, [Perlmutter](https://docs.nersc.gov/systems/perlmutter/architecture/)) and communicate with it from another job.

The vLLM server is purposefully API compatible with OpenAI, meaning that you can easily port code that relies on the [OpenAI API](https://github.com/openai/openai-python).

## Usage

You will find the SLURM script to get the server started in the [scripts](./scripts/) folder.

You will also find a number of Python demo scripts (locating the server then talking to it) in this folder. To run them, install the following environment:

```sh
module load python
python3 -m venv venv
source venv/bin/activate
python3 -m pip install openai rich
```

To run a script (for example the chat interface), you will need to load Python and activate the environment:

```sh
module load python
source venv/bin/activate
python3 chat.py
```

## Demo Scripts

* [`chat.py`](./chat.py): simple chatbot demo, letting you talk to the model.
* [`judge.py`](./judge.py): a judge model demonstrating more advanced generation (prefilling the beginning of an answer to enforce a chain-of-thought, then forcing it to name one of several provided answers).
* [`embedding.py`](./embedding.py): a demo of the embedding functionality.
* [`all.py`](./all.py): tries accessing both llm and embedding type of functionalities via the router.

See [vLLM's OpenAI frontend documentation](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) for a discussion of the available generation options (you can enforce a json output format, stop the generaiton on a given keyword, etc.).

You will find a quickstart example [here](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-chat-completions-api-with-vllm), and a number of examples [there](https://docs.vllm.ai/en/latest/getting_started/examples/examples_index.html).

## Inner-Workings

### LLM

The vLLM-openai container provides an OpenAI compatible API.
We run it with Shifter, dpeloying it to a node using SLURM.

The worker is located by its name and group (`vllm_worker` and `nstaff`) then talk to via its `hostname:port`.

Any script that works with the OpenAI API should be portable, using the [provided bit of code](./nerschat/__init__.py) to find the base url of a currently running worker.

[Huggingface's Text Generation Inference](https://github.com/huggingface/text-generation-inference) is one promising backend alternative we have not explored. It has a reputation for being slower / less efficient than vLLM but supporting a wider range of models.

### Embeddings

In theory, vLLM allows serving embeddings but they currently (November 2024) do not support common architectures (like Bert) nor take into account the fact that some models add prefixes to text depending on use case (i.e. a question and a bit of knowledge should be embedded differently).

Thus, we defaulted to [Huggingface's Text Embeddings Inference](https://github.com/huggingface/text-embeddings-inference).

See [this page](https://huggingface.co/docs/text-embeddings-inference/quick_tour) for the various supported enpoints (the API is further detailled [here](https://huggingface.github.io/text-embeddings-inference/)).

### Router

Since we can only serve one model (and one type of model) per worker, there is a `router` script that puts a simple `nginx` router on top of two workers, redirecting queries depending on their routes (embedding or LLM?).

## TODO

Functionalities:

* compose several containers?
  * this is a usecase for docker compose / rancher
    * an easy solution would be a lightweight router: starting several vllm on different port and routing commands to them
    * or... we launch as many workers as we want and a router periodically check which models are available and takes/redirects requests
    * or, we could create a router at the client level, sending feelers for the various workers and redirecting as needed
* connection might fail if the node has not loaded the model yet, give it some (2-5minutes) time (and have a nice error)?
* try reconnecting / finding a new worker if the current one died?

Testing:

* is it possible to contact a worker from outside the cluster?
