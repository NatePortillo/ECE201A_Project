# Class Imports
import sys
import os
import ast

from utilities.gpt4 import GPT4
from utilities.syntaxprocessor import SyntaxProcessor
from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130

from utilities.display import Display
from utilities.utils import retry_function, extract_function_parameters
from utilities.prompts import STRICT_SYNTAX_INSTRUCT
USER_PROMPT = "Create a strong-arm latch using interdigitated placement to match the cross-coupled inverters"

def generate_strictsyntax_and_process():
    gpt4 = GPT4(api_key="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")
    map = SyntaxProcessor()

    # Generate new strict_syntax
    strict_syntax = gpt4.gpt_4o_strict_syntax(USER_PROMPT, STRICT_SYNTAX_INSTRUCT)
    print(f"Generated strict_syntax: {strict_syntax}")

    # Process the strict syntax
    return map.process_syntax(strict_syntax)

try:
    result = retry_function(
        generate_strictsyntax_and_process, 
        max_retries=10, 
        delay=2
    )
    print(f"Function succeeded with result: {result}")
except Exception as e:
    print(f"Function ultimately failed after retries: {e}")

# Save the generated Python code to a file
with open("generated_layout.py", "w") as f:
    f.write(result)

# Extract the parameters from layout_call function
from generated_layout import layout_cell
parameters = extract_function_parameters(layout_cell)

def generate_parameters_and_process():
    gpt4 = GPT4(api_key="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")
    response = gpt4.gpt_4o_parameters(USER_PROMPT, parameters)
    parsed_response = ast.literal_eval(response)  # Convert string to Python list
    return parsed_response

# Do multiple tries until prompting is refined
try:
    parsed_response = retry_function(
        generate_parameters_and_process, 
        max_retries=10, 
        delay=2
    )
    print(f"Function succeeded with result: {parsed_response}")
except Exception as e:
    print(f"Function ultimately failed after retries: {e}")

# Create a dictionary of parameter values
param_values = {param['name']: param['value'] for param in parsed_response}
print(param_values)
# Ensure 'pdk' references the actual object if needed
param_values['pdk'] = sky130  # Replace "MappedPDK" string with the actual object
layout = layout_cell(**param_values)

display = Display()

with display.left:
  display.display_component(layout, scale=2.5)

# Delete the layout file
os.remove('generated_layout.py')