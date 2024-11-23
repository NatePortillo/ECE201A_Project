import re
from glayout.flow.pdk.mappedpdk import MappedPDK
from glayout.flow.primitives import fet
from glayout.flow.routing import smart_route
from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130
from glayout.syntaxer.process_input import GlayoutCode

from knowledge_graph.kg import ComponentKnowledgeGraph

class SyntaxProcessor:
    """
    A class for processing layout strict syntax commands into executable layout code.

    This class processes user-provided commands in a strict syntax format to 
    generate layout code using the GlayoutCode library. It supports commands for 
    importing components, creating parameters, placing devices, and moving components.

    Attributes:
        layout_code (GlayoutCode): An instance of GlayoutCode for managing the layout syntax and code generation.
    """
    def __init__(self, toplvl_name="layout"):
        """
        Initializes the SyntaxProcessor with a top-level layout name.
        """
        self.layout_code = GlayoutCode(toplvl_name)
        self.kg_drive = ComponentKnowledgeGraph("neo4j+s://37447c78.databases.neo4j.io",
                                                "neo4j",
                                                "cUoYzRehyPFlauBOhekoJolfVDVUOGrTuAwLIZywZy4")

    def parse_command(self, command, pdk):
        """
        Parses and processes a single layout command following StrictSyntax format.

        Supports the following commands:
            - `import`: Imports a component into the layout.
            - `create`: Creates a parameter with a specified type and name.
            - `place`: Places a component with specified attributes.
            - `move`: Moves a component relative to another component.
            -'route': Does not currently work.

        Args:
            command (str): The strict syntax command to parse.
            pdk (MappedPDK): The process design kit (PDK) object for the layout.
        """
        command = command.strip()

        if command.startswith("import"):
            # Example: import CrossCoupledInverters
            match = re.match(r"import (\w+)", command)
            if match:
                component_name = match.group(1)
                if(self.kg_drive.is_valid_import(component_name)):
                    self.layout_code.update_import_table([component_name], component_name)
                    return component_name, True 
                else:
                    return component_name, False
            else:
                raise ValueError(f"Unable to parse import command: {command}")
        
        elif command.startswith("create"):
            # Example: create a float parameter called width
            match = re.match(r"create a (\w+) parameter called (\w+)", command)
            if match:
                vartype, varname = match.groups()
                vartype = float if vartype == "float" else int
                self.layout_code.update_parameter_table(varname, vartype)
            else:
                raise ValueError(f"Unable to parse import command: {command}")

        elif command.startswith("place"):
            # Example: place a nmos called inv1_N with width=1.5, length=0.5, fingers=4
            match = re.match(r"place a (\w+(?: \w+)?) called (\w+)(?: with (.+))?", command)
            if match:
                generator_id, component_name, params = match.groups()
                params_dict = {}
                if params:
                    try:
                        for param in params.split(","):
                            if "=" in param:
                                key, value = param.split("=", 1)  # Split only on the first '='
                                params_dict[key.strip()] = value.strip()
                            else:
                                print(f"Skipping invalid parameter: {param}")
                        params_str = ", ".join(f"{key} = {value}" for key, value in params_dict.items()) # Convert params_dict to a string for `user_input_parameters`
                    except Exception as e:
                        raise ValueError(f"Error parsing parameters for 'place' command: {params}. Error: {e}")
                else:
                    params_str = "" # Handle cases with no parameters
                self.layout_code.update_place_table(generator_id=generator_id, component_name=component_name, user_input_parameters=params_str)
            else:
                raise ValueError(f"Could not parse 'place' command: {command}")

        elif command.startswith("move"):
            # Example: move latch_B2 below latch_B1 or move mirror to the right of reference
            match = re.match(r"move (\w+)(?: to the)? (right|left|above|below)(?: of)? (\w+)", command)
            if match:
                comp_to_move, direction, ref_comp = match.groups()
                comp_to_move = comp_to_move.strip()
                direction = direction.strip()
                ref_comp = ref_comp.strip()
                print(f"Parsed move command: comp_to_move='{comp_to_move}', direction='{direction}', ref_comp='{ref_comp}'")
                self.layout_code.update_move_table("relative", comp_to_move, ref_comp, direction)
            else:
                raise ValueError(f"Unable to parse move command: {command}")

        elif command.startswith("route"):
            # Example: route between inv1_N_drain and inv2_N_gate using smart_route
            match = re.match(r"route between (\w+) and (\w+) using (\w+)", command)
            if match:
                port1, port2, route_type = match.groups()
                self.layout_code.update_route_table(port1, port2, "", route_type)
        
        return None, True

    def process_syntax(self, strict_syntax, pdk=sky130):
        """
        Processes a block of strict syntax commands into layout code.

        This method splits the strict syntax input into individual commands and
        processes each using `parse_command`.

        Args:
            strict_syntax (str): A block of strict syntax commands separated by newlines.
            pdk (MappedPDK, optional): The process design kit (PDK) object. Defaults to sky130.
        """
        commands = strict_syntax.strip().split("\n")
        for command in commands:
            component, passed = self.parse_command(command, pdk)
            if not passed:
                return component, False
            
        return self.layout_code.get_code(), True