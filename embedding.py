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

# text-embedding-inference does not provide a list a model, nor care for that parameter
model='EMPTY'

#--------------------------------------------------------------------------------------------------
# DEMO

# Sentences to embed
sentences = ["How can I connect to Perlmutter?", "You can use SSH to connect to Perlmutter."]

# running the embedder
responses = client.embeddings.create(model=model, input=sentences)
embeddings = [data.embedding for data in responses.data] # lists of floats

# displaying results
for embedding in embeddings:
  print(f"type:{type(embedding)} len:{len(embedding)}")

# display similarity
dot = sum( (e1*e2) for (e1,e2) in zip(embeddings[0], embeddings[1]) )
print(f"dot product: {dot}")