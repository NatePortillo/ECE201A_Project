# Class Imports
import sys
import os
import ast
# import pdb
from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130

from utilities.display import Display
from utilities.utils import retry_function, extract_function_parameters, generate_strictsyntax_and_process, generate_parameters_and_process

from prompts import USER_PROMPT, FEEDBACK

try:
    result = retry_function(
        generate_strictsyntax_and_process, 
        max_retries=10, 
        delay=2
    )
    print(f"Function succeeded with result: {result}")
except Exception as e:
    print(f"Function ultimately failed after retries: {e}")

with open("generated_layout.py", "w") as f: # Save the generated Python code to a file
    f.write(result)

from generated_layout import layout_cell # Extract the parameters from layout_call function
parameters = extract_function_parameters(layout_cell)

try:
    parsed_response = retry_function(
        generate_parameters_and_process, 
        10, 
        2,
        parameters
    )
    print(f"Function succeeded with result: {parsed_response}")
except Exception as e:
    print(f"Function ultimately failed after retries: {e}")

param_values = {param['name']: param['value'] for param in parsed_response} # Create a dictionary of parameter values
param_values['pdk'] = sky130  # Replace "MappedPDK" string with the actual object
layout = layout_cell(**param_values)

display = Display()
with display.left:
  display.display_component(layout, scale=2.5)

print("Your device has been created. Here are current input parameters: ")
for res_params in param_values.keys():
    if res_params != 'pdk':
        print(res_params,": ", param_values[res_params]) # Print current parameters generated

parameter_feedback = input("Feedback for the layout parameters? If none, please press enter: \n")
while(parameter_feedback):
    USER_PROMPT = USER_PROMPT +"\n"+ parameter_feedback
    print(USER_PROMPT)
    
    FEEDBACK = FEEDBACK + parameter_feedback
    print(FEEDBACK)

    try:
        parsed_response = retry_function(
            generate_parameters_and_process, 
            10, 
            2,
            param_values,
            FEEDBACK
        )
        print(f"Function succeeded with result: {parsed_response}")
    except Exception as e:
        print(f"Function ultimately failed after retries: {e}")

    param_values = {param['name']: param['value'] for param in parsed_response} # Create a dictionary of parameter values
    param_values['pdk'] = sky130  # Replace "MappedPDK" string with the actual object
    layout = layout_cell(**param_values)


    display = Display()
    with display.left:
        display.display_component(layout, scale=2.5)

    os.remove('generated_layout.py') # Delete the layout file

    print("Here are the parameters:")
    for res_params in param_values.keys():
        if res_params != 'pdk':
            print(res_params,": ", param_values[res_params])
    parameter_feedback = input("Feedback for the layout ?, if none, please press enter: \n")
