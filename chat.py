import random
import subprocess
from openai import OpenAI
from rich.markdown import Markdown
from rich.console import Console

WORKER_NAME = "vllm_server"
ACCOUNT_NAME = "nstaff,nstaff_g"
PORT=8000
API_KEY = "EMPTY"

#--------------------------------------------------------------------------------------------------
# FINDING THE NERSC WORKER

def find_chatbot_worker_node(job_name=WORKER_NAME, account_name=ACCOUNT_NAME):
    """
    Find the hostname of the SLURM node running the job called `chatbot_worker` under a specific account.
    Returns a randomly selected node if multiple matching jobs are running.
    """
    try:
        # Run the squeue command to list SLURM jobs and filter by job name, account, and running state
        result = subprocess.run(
            [
                "squeue",
                "--name", job_name,
                "--account", account_name,
                "--states", "RUNNING",
                "--noheader",
                "-o", "%N"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Get all running instances and randomly select one
        running_nodes = [node for node in result.stdout.strip().splitlines() if node]
        if not running_nodes:
            raise RuntimeError(f"No running job with name '{job_name}' found under account '{account_name}'.")
            
        # Randomly select one node if multiple are found
        node_name = random.choice(running_nodes)
        return node_name
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error finding job '{job_name}' under account '{account_name}': {e.stderr}")

#--------------------------------------------------------------------------------------------------
# SET-UP

# Creates an OpenAI client on top of our vLLM server.
hostname = find_chatbot_worker_node(job_name=WORKER_NAME, account_name=ACCOUNT_NAME)
base_url = f"http://{hostname}:{PORT}/v1"
client = OpenAI(api_key=API_KEY, base_url=base_url)
print(f"Created an OpenAI client for at {base_url} (hostname:{hostname})")

# Finds the model available
models = client.models.list()
model = models.data[0].id # vLLM allows only one model
model_name = model[model.rfind('/')+1:]
print(f"Model used: {model_name}")

#--------------------------------------------------------------------------------------------------
# CHAT INTERFACE

def display_logo():
    """Displays a fancy ascii art logo"""
    logo = "\n\
░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░▒▓████████▓▒░\n\
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░\n\
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░\n\
░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░      ░▒▓████████▓▒░▒▓████████▓▒░ ░▒▓█▓▒░\n\
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░\n\
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░\n\
░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░"
    print(logo)                                                                                       

def get_answer(messages)->str:
    chat_completion = client.chat.completions.create(model=model, messages=messages)
    answer=chat_completion.choices[0].message.content
    return answer

def chat():
    display_logo()
    messages = []
    console = Console()
    print()
    while True:
        # gets user input
        question = input("> ")
        messages.append({'role':'user', 'content': question})
        # gets an answer and stores it
        answer = get_answer(messages)
        answer_message = {'role':'assistant', 'content': answer}
        messages.append(answer_message)
        # pretty prints the answer
        markdown_answer = Markdown(answer_message['content'])
        print()
        console.print(markdown_answer)
        print()

# Runs a chat
chat()