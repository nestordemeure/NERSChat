from nerschat import generate_api_url
from openai import OpenAI
from rich.markdown import Markdown
from rich.console import Console

WORKER_NAME = "router_vllm_server"
ACCOUNT_NAME = "nstaff,nstaff_g"
PORT=8000
API_KEY = "EMPTY"
API_URL=generate_api_url(WORKER_NAME, ACCOUNT_NAME, PORT)

#--------------------------------------------------------------------------------------------------
# SET-UP

# Creates an OpenAI client on top of our vLLM server.
client = OpenAI(api_key=API_KEY, base_url=API_URL)
print(f"Found an OpenAI client at {API_URL}")

# Finds the model available
models = client.models.list()
model = models.data[0].id # vLLM allows only one model
model_name = model[model.rfind('/')+1:]
print(f"Model used: {model_name}")

#--------------------------------------------------------------------------------------------------
# TESTS

messages = [{'role':'user', 'content': 'what is the capital of France?'}]
chat_completion = client.chat.completions.create(model=model, messages=messages)
answer=chat_completion.choices[0].message.content
print(f"answer: {answer}")

sentences = ["How can I connect to Perlmutter?", "You can use SSH to connect to Perlmutter."]
responses = client.embeddings.create(model=model, input=sentences)
embeddings = [data.embedding for data in responses.data]
dot = sum( (e1*e2) for (e1,e2) in zip(embeddings[0], embeddings[1]) )
print(f"dot product: {dot}")
