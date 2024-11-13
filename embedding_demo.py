from nerschat import generate_api_url
from openai import OpenAI

WORKER_NAME = "embedding_vllm_server"
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
# DEMO

# Sentences to embed
sentences = ["Hello my name is", "The best thing about vLLM is that it supports many different models"]

# running the embedder
responses = client.embeddings.create(model=model, input=sentences)
embeddings = [data.embedding for data in responses.data] # lists of floats

# displaying results
for embedding in embeddings:
  print(f"type:{type(embedding)} value:{embedding}")
