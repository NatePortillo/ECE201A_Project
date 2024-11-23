import time
import inspect
import ast

from utilities.gpt4 import GPT4
from utilities.syntaxprocessor import SyntaxProcessor
from prompts import STRICT_SYNTAX_INSTRUCT, USER_PROMPT, API_KEY

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
    """
    Generates and processes strict syntax using GPT-4 and a syntax processor.
    Dynamically fetches relevant data using RAGs and retries if processing fails.

    Returns:
        str: The processed strict syntax as a string.

    Raises:
        Exception: If all attempts to process the syntax fail.
    """
    gpt4 = GPT4(api_key=API_KEY)
    syntax_processor = SyntaxProcessor()
    
    # Step 1: Generate initial strict syntax
    strict_syntax = gpt4.gpt_4o_strict_syntax(
        USER_PROMPT,
        STRICT_SYNTAX_INSTRUCT,
        parse_embeddings(df=DF_ANALOG, input_prompt=USER_PROMPT),
        parse_embeddings(df=DF_CONVOS, input_prompt=USER_PROMPT)
    )
    print(strict_syntax)

    # Step 2: Process the strict syntax
    component, passed = syntax_processor.process_syntax(strict_syntax)
    if passed:
        return component  # Successfully processed code

    # Step 3: Handle invalid component
    print(f"Invalid component found: {component}")
    kg_components = syntax_processor.kg_drive.get_all_components()
    close_matches = syntax_processor.kg_drive.suggest_string_based_alternatives(component, kg_components)
    close_match_dependencies = syntax_processor.kg_drive.query_dependencies(close_matches)
    all_legal_imports = syntax_processor.kg_drive.get_all_components_with_dependencies()

    # Step 4: Generate feedback prompt with suggestions
    strict_syntax_fb = gpt4.gpt_4o_comp_feedback(
        USER_PROMPT,
        STRICT_SYNTAX_INSTRUCT,
        parse_embeddings(df=DF_ANALOG, input_prompt=USER_PROMPT),
        parse_embeddings(df=DF_CONVOS, input_prompt=USER_PROMPT),
        close_matches,
        close_match_dependencies,
        all_legal_imports
    )
    print(strict_syntax_fb)
    # Step 5: Retry processing the feedback-generated syntax
    component, passed = syntax_processor.process_syntax(strict_syntax_fb)
    if passed:
        return component

    # If processing still fails, raise an error
    raise Exception(f"Failed to process strict syntax even after retries. Invalid component: {component}")

def generate_parameters_and_process(parameters):
    """
    Generates and processes parameters (parameter values) for a layout function using GPT-4.

    This function sends a user prompt and a set of extracted parameters to the GPT-4 API.
    The response is expected to be a string representation of a Python list, which is parsed
    into a usable Python object.

    Args:
        parameters (list): A list of parameters to guide GPT-4 in generating the response.

    Returns:
        list: A parsed list of parameters generated by GPT-4.

    Raises:
        ValueError: If the GPT-4 response cannot be parsed into a Python list.
        Exception: If the GPT-4 API call fails or returns an unexpected response.
    """
    gpt4 = GPT4(api_key=API_KEY)
    response = gpt4.gpt_4o_parameters(USER_PROMPT, parameters)
    parsed_response = ast.literal_eval(response)  # Convert string to Python list
    
    return parsed_response