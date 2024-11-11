import random
import subprocess

# default job parameters
DEFAULT_WORKER_NAME = "vllm_server"
DEFAULT_ACCOUNT_NAME = "nstaff,nstaff_g"
DEFAULT_PORT=8000

def find_hostname(job_name:str, account_name:str) -> str:
    """
    Find the hostname of the SLURM node running the job called `job_name` under the `account_name` account.
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

def generate_api_url(job_name:str=DEFAULT_WORKER_NAME, account_name:str=DEFAULT_ACCOUNT_NAME, port:int=DEFAULT_PORT) -> str:
    """
    Generates the base url at which the OpenAI-like API will be located.
    Default to a job called `DEFAULT_WORKER_NAME`, running under `DEFAULT_ACCOUNT_NAME`, and listening on port `DEFAULT_PORT`
    """
    hostname = find_hostname(job_name, account_name)
    base_url = f"http://{hostname}:{port}/v1"
    return base_url
