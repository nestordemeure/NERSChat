# NERSChat: A SLURM-based Chatbot Worker

This code lets you deploy a [container-based vLLM server](https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html) on a SLURM cluster (specifically, Perlmutter) and communicate with it from another job.

The vLLM server is purposefully API compatible with OpenAI, meaning that you can easily port code that relies on the OpenAI API.

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

See [vLLM's OpenAI frontend documentation](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) for a discussion of the available generation options (you can enforce a json output format, stop the generaiton on a given keyword, etc.).

You will find a quickstart example [here](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#openai-chat-completions-api-with-vllm), and a number of examples [there](https://docs.vllm.ai/en/latest/getting_started/examples/examples_index.html).

## Inner-Workings

The vLLM-openai container provides an OpenAI compatible API.
We run it with Shifter, dpeloying it to a node using SLURM.

The worker is located by its name and group (`vllm_worker` and `nstaff`) then talk to via its hostname:port.

Any script that works with the OpenAI API should be portable, using the provided bit of code to find base url of a running worker.

## TODO

Functionalities:

* set-up a multi nodes worker.
* compose several containers?
* connection might fail if the node has not loaded the model yet, give it some (2-5minutes) time (and have a nice error)?
* try reconnecting / finding a new worker if the current one died?

Testing:

* is it possible to contact a worker from outside the cluster?

Links:

* you *cannot* serve several models in the same instance, but you can serve individual models seperatly and have a front-end on top (see [here](https://docs.vllm.ai/en/v0.6.0/serving/faq.html)). Docker compose might be a way forward.
