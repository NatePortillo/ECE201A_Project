import os
import json

def create_json_from_folder(input_folder, output_json_file):
    """
    Reads all files in the input folder and creates a JSON file mapping file names to file contents.

    Args:
        input_folder (str): Path to the folder containing the files.
        output_json_file (str): Path to save the generated JSON file.
    """
    file_data = {}

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        if os.path.isfile(file_path):
            component_name = os.path.splitext(file_name)[0]

            with open(file_path, 'r') as file:
                content = file.read()

            file_data[component_name] = content

    with open(output_json_file, 'w') as json_file:
        json.dump(file_data, json_file, indent=4)

    print(f"JSON file created successfully at {output_json_file}")

input_folder = r"C:\Users\natha\Desktop\ECE201A_Project\RAG\analog_design" 
output_json_file = "analog.json" 
create_json_from_folder(input_folder, output_json_file)
