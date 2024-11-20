import time
import inspect
import ast

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