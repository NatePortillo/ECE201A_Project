import os
import json
from collections import defaultdict

def parse_syntax_file(file_path):
    """
    Parse a strict syntax file to extract the top-level component and its imports.
    """
    unique_component = None
    imports = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if unique_component is None and line:  # First non-empty line is the component name
                unique_component = line
            elif line.startswith("import"):
                _, imported_component = line.split()
                imports.append(imported_component)

    return unique_component, imports


def process_all_files(folder_path):
    """
    Process all strict syntax files in a folder and generate a JSON representation
    of unique components and their imports.
    """
    components_graph = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".convo"):  # Assuming syntax files have a .txt extension
            file_path = os.path.join(folder_path, file_name)
            unique_component, imports = parse_syntax_file(file_path)
            if unique_component:  # Only add if a valid component name is found
                components_graph[unique_component] = imports

    return components_graph


def save_to_json(data, output_file):
    """
    Save the processed graph data to a JSON file.
    """
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)


# Main script execution
if __name__ == "__main__":
    folder_path = r"C:\Users\natha\Desktop\ECE201A_Project\RAG\foundational_convos"  # Replace with your folder path
    output_file = "component_graph.json"

    components_graph = process_all_files(folder_path)
    save_to_json(components_graph, output_file)
    print(f"Component graph saved to {output_file}")
