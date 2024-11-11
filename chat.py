from nerschat import generate_api_url
from openai import OpenAI
from rich.markdown import Markdown
from rich.console import Console

WORKER_NAME = "large_vllm_server"
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