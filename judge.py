from nerschat import generate_api_url
from openai import OpenAI
from rich.markdown import Markdown
from rich.console import Console

WORKER_NAME = "vllm_server"
ACCOUNT_NAME = "nstaff,nstaff_g"
PORT=8000
API_KEY = "EMPTY"
API_URL=generate_api_url(WORKER_NAME, ACCOUNT_NAME, PORT)

#--------------------------------------------------------------------------------------------------
# SET-UP

# Creates an OpenAI client on top of our vLLM server.
client = OpenAI(api_key=API_KEY, base_url=API_URL)
print(f"Created an OpenAI client for at {API_URL}")

# Finds the model available
models = client.models.list()
model = models.data[0].id # vLLM allows only one model
model_name = model[model.rfind('/')+1:]
print(f"Model used: {model_name}")

#--------------------------------------------------------------------------------------------------
# JUDGING CODE

JUDGING_PROMPT = """
Please act as an impartial judge and evaluate the quality of the responses provided by two AI assistants to the user question displayed below.  

[User Question]
{QUESTION}

[The start of Answer #1]
{ANSWER1}
[The end of Answer #1]

[The start of Answer #2]
{ANSWER2}
[The end of Answer #2]

Your task is to determine which of the two answers is better, based on the following criteria:
- Choose the response that follows the user’s instructions and answers the user’s question better.
- Evaluate based on helpfulness, relevance, accuracy, depth, creativity, and level of detail of the responses.
- Do not allow the length or order of the responses to influence your evaluation.

In 1 paragraph, write out your thought process and reasoning for which answer better meets the criteria. Do not actually answer the original question yourself. You are only choosing between the two provided answers based on how well they meet the specified criteria. If both answers are comparable such that you have no preference, then explain that.
"""

def judging(question:str, answer1:str, answer2:str):
    """
    Given a quesiton and two potential answers, picks the best one.
    """
    # generate the main prompt
    prompt = JUDGING_PROMPT.format(QUESTION=question, ANSWER1=answer1, ANSWER2=answer2)

    # manually start the model's answer to forcefully get into a chain-of-thought.
    answer_prefix = "Let me think about the pros and cons of each answer first."
    generation_parameters = {"add_generation_prompt":False, "continue_final_message":True}
    # submit the message
    messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': answer_prefix}]
    # get the answer
    chat_completion = client.chat.completions.create(model=model, messages=messages, extra_body=generation_parameters)
    reasonning = chat_completion.choices[0].message.content
    
    # force the generation to be one of the required answers
    answer_prefix = reasonning + '\n\n' + "Thus, I believe the best answer is "
    generation_parameters = {"add_generation_prompt":False, "continue_final_message":True, 
                             "guided_choice": ["Answer #1", "Answer #2"]}
    messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': answer_prefix}]
    # generate the answer
    chat_completion = client.chat.completions.create(model=model, messages=messages, extra_body=generation_parameters)
    answer = chat_completion.choices[0].message.content[len(answer_prefix):] # extracting the new tokens only

    # return the result
    return reasonning, answer

#--------------------------------------------------------------------------------------------------
# DEMO

question = "How can I connect to the Perlmutter supercomputer?"
answer1 = "You should totally use SSH!"
answer2 = "I am sorry Dave, I cannot do that for you."
print(f"\nQuestion: `{question}`")
print(f"\nAnswer #1: `{answer1}`")
print(f"\nAnswer #2: `{answer2}`")

reasonning, answer = judging(question, answer1, answer2)
print(f"\nReasonning:\n\n```\n{reasonning}\n```")
print(f"\nAnswer: {answer}")