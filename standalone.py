import time
import argparse
from functools import wraps
from openai import OpenAI

#--------------------------------------------------------------------------------------------------
# SET-UP

def retry(func, max_retries=5, initial_wait=30, backoff_factor=2):
    """
    Creates a new function that wraps `func` with retry logic.

    :param func: The function to wrap with retry logic.
    :param max_retries: Maximum number of retries.
    :param initial_wait: Initial wait time in seconds for exponential backoff.
    :param backoff_factor: Factor by which the wait time is multiplied after each failure.
    :return: A new function with retry logic.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        wait_time = initial_wait

        for attempt in range(max_retries):
            try:
                # Attempt to execute the function
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    wait_time *= backoff_factor  # Exponential backoff
                else:
                    print(f"Attempt {attempt + 1} failed: {e}. No more retries left.")
                    raise  # Re-raise the exception if max retries are exceeded

    return wrapper

def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Client for a given model server.")

    # Add arguments
    parser.add_argument("--host", type=str, required=True, help="Hostname or IP address of the server.")
    parser.add_argument("--port", type=int, required=True, help="Port number the server will listen on.")
    parser.add_argument("--api-key", type=str, default="EMPTY", help="API key for authentication. Defaults to 'EMPTY' if not provided.")
    
    # Return parsed arguments
    return parser.parse_args()

def get_client(args):
    """
    Gets an OpenAI API and the associated model.
    
    NOTE: the calls to `retry` are there to wait if needed while the model is still loading.
    """
    # generating the API url
    base_url = f"http://{args.host}:{args.port}/v1"
    print(f"Looking for API at {base_url}")

    # Creates an OpenAI client on top of our vLLM server.
    client = retry(OpenAI)(api_key=args.api_key, base_url=base_url)
    print(f"Found an OpenAI-style API.")

    # Finds the model available
    models = retry(client.models.list)()
    model = models.data[0].id # vLLM allows only one model
    model_name = model[model.rfind('/')+1:]
    print(f"Using model {model_name}")

    # check the model
    retry(client.chat.completions.create)(model=model, messages=[{'role': 'user', 'content': "Say Hi!"}])
    print("Confirmed the client is running.")

    return (client, model)

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
- Choose the response that follows the user's instructions and answers the user's question better.
- Evaluate based on helpfulness, relevance, accuracy, depth, creativity, and level of detail of the responses.
- Do not allow the length or order of the responses to influence your evaluation.

In 1 paragraph, write out your thought process and reasoning for which answer better meets the criteria. Do not actually answer the original question yourself. You are only choosing between the two provided answers based on how well they meet the specified criteria. If both answers are comparable such that you have no preference, then explain that.
"""

def judging(client, model:str, question:str, answer1:str, answer2:str):
    """
    Given a question and two potential answers, picks the best one.
    """
    # generate the main prompt
    prompt = JUDGING_PROMPT.format(QUESTION=question, ANSWER1=answer1, ANSWER2=answer2)

    # prefix the model's answer to forcefully get into a chain-of-thought
    answer_prefix = "Let me think about the pros and cons of each answer first."
    generation_parameters = {"add_generation_prompt":False, "continue_final_message":True}
    # submit the message
    messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': answer_prefix}]
    # get the answer
    chat_completion = client.chat.completions.create(model=model, messages=messages, extra_body=generation_parameters)
    reasonning = chat_completion.choices[0].message.content
    
    # force the further generation to be one of the required answers
    answer_prefix = reasonning + '\n\n' + "Thus, I believe the best answer is "
    generation_parameters = {"add_generation_prompt":False, "continue_final_message":True, "guided_choice": ["Answer #1", "Answer #2"]}
    messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': answer_prefix}]
    # generate the answer
    chat_completion = client.chat.completions.create(model=model, messages=messages, extra_body=generation_parameters)
    answer = chat_completion.choices[0].message.content[len(answer_prefix):] # extracting the new tokens only

    # return the result
    return reasonning, answer

#--------------------------------------------------------------------------------------------------
# DEMO

def main():
    # Parse arguments
    args = parse_arguments()

    # Get the API client
    (client,model) = get_client(args)

    # judging demo
    question = "How can I connect to the Perlmutter supercomputer?"
    answer1 = "You should totally use SSH!"
    answer2 = "I'm sorry, Dave. I'm afraid I can't do that"
    print(f"\nQuestion: `{question}`")
    print(f"\nAnswer #1: `{answer1}`")
    print(f"\nAnswer #2: `{answer2}`")

    reasonning, answer = judging(client, model, question, answer1, answer2)
    print(f"\nReasonning:\n\n```\n{reasonning}\n```")
    print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main()
