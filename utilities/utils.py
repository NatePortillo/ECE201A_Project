import time
import inspect
import ast

from utilities.gpt4 import GPT4
from utilities.syntaxprocessor import SyntaxProcessor
from utilities.prompts import STRICT_SYNTAX_INSTRUCT, USER_PROMPT, API_KEY

from RAG.search_embeddings import parse_embeddings, DF_ANALOG, DF_CONVOS

def retry_function(func, max_retries=3, delay=1, *args, **kwargs):
    """
    Retries a function multiple times if it raises an exception.
    
    Args:
        func (callable): The function to call.
        max_retries (int): Maximum number of retries.
        delay (float): Delay (in seconds) between retries.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
        
    Returns:
        The return value of the function, if successful.
    
    Raises:
        The last exception raised by the function, if all retries fail.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed.")
                raise

def extract_function_parameters(func):
    """
    Extract parameter names, types, and default values from a function.
    
    Args:
        func (function): The function to analyze.
    
    Returns:
        dict: A dictionary with parameter names, types, and default values.
    """
    # Get the source code of the function
    source = inspect.getsource(func)
    # Parse the function using the AST module
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            parameters = {}
            for arg in node.args.args:
                # Extract the parameter name
                param_name = arg.arg
                # Extract the type hint if available
                if arg.annotation:
                    param_type = ast.dump(arg.annotation)
                else:
                    param_type = "No Type"
                # Extract the default value if available
                default_value = None
                if arg.arg in {d.arg for d in node.args.defaults if isinstance(d, ast.arg)}:
                    default_value = node.args.defaults[arg.arg]
                parameters[param_name] = {
                    "type": param_type,
                    "default": default_value,
                }
            return parameters
    return {}

def generate_strictsyntax_and_process():
    gpt4 = GPT4(api_key=API_KEY)
    map = SyntaxProcessor()
    strict_syntax = gpt4.gpt_4o_strict_syntax(USER_PROMPT, # Generate new strict_syntax
                                              STRICT_SYNTAX_INSTRUCT, 
                                              parse_embeddings(df=DF_ANALOG, input_prompt=USER_PROMPT),
                                              parse_embeddings(df=DF_CONVOS, input_prompt=USER_PROMPT))
    
    return map.process_syntax(strict_syntax) # Process the strict syntax

def generate_parameters_and_process(parameters):
    gpt4 = GPT4(api_key=API_KEY)
    response = gpt4.gpt_4o_parameters(USER_PROMPT, parameters)
    parsed_response = ast.literal_eval(response)  # Convert string to Python list
    
    return parsed_response