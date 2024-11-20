from glayout.flow.pdk.mappedpdk import MappedPDK
from glayout.flow.primitives import fet
from glayout.flow.routing import smart_route
from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130
from glayout.syntaxer.process_input import GlayoutCode

class SyntaxProcessor:
    def __init__(self, toplvl_name="layout"):
        self.layout_code = GlayoutCode(toplvl_name)

    def parse_command(self, command, pdk):
        """
        Parse a single strict syntax command and update GlayoutCode.
        """
        if command.startswith("create"):
            # Example: create a float parameter called width
            _, _, vartype, _, _, varname = command.split()
            vartype = float if vartype == "float" else int
            self.layout_code.update_parameter_table(varname, vartype)

        elif command.startswith("place"):
            # Example: place a nmos called inv1_N with width=1.5, length=0.5, fingers=4
            parts = command.split(" ")
            generator_id = parts[2]  # e.g., 'nmos'
            component_name = parts[4]  # e.g., 'inv1_N'
            params = " ".join(parts[6:])  # e.g., 'width=1.5, length=0.5, fingers=4'
            self.layout_code.update_place_table(generator_id, params, component_name)

        elif command.startswith("move"):
            # Example: move latch_B2 below latch_B1
            parts = command.split(" ")
            comp_to_move = parts[1]  # e.g., 'inv1_N'
            direction = parts[2]  # e.g., 'left'
            ref_comp = parts[3]  # e.g., 'inv2_N'
            self.layout_code.update_move_table("relative", comp_to_move, ref_comp, direction)

        #elif command.startswith("route"):
            # Example: route between inv1_N_drain and inv2_N_gate using smart_route
        #    parts = command.split(" ")
        #    port1 = parts[2]  # e.g., 'inv1_N_drain'
        #    port2 = parts[4]  # e.g., 'inv2_N_gate'
        #    route_type = parts[-1]  # e.g., 'smart_route'
        #    self.layout_code.update_route_table(port1, port2, "", route_type)

    def process_syntax(self, strict_syntax, pdk=sky130):
        """
        Process a block of strict syntax commands.
        """
        commands = strict_syntax.strip().split("\n")
        for command in commands:
            self.parse_command(command, pdk)
        return self.layout_code.get_code()
