from glayout.flow.primitives.fet import nmos
from glayout.flow.pdk.sky130_mapped import sky130_mapped_pdk as sky130
from glayout.flow.pdk.gf180_mapped import gf180_mapped_pdk as gf180
import gdstk
import svgutils.transform as sg
import IPython.display
from IPython.display import clear_output
import ipywidgets as widgets

class Display:
    def __init__(self):
        # Initialize instance-specific outputs
        self.left = widgets.Output()
        self.leftSPICE = widgets.Output()
        self.right = widgets.Output()
        self.rightSPICE = widgets.Output()
        self.hide = widgets.Output()

        # Create a grid layout
        self.grid = widgets.GridspecLayout(1, 4)
        self.grid[0, 0] = self.left
        self.grid[0, 1] = self.leftSPICE
        self.grid[0, 2] = self.right
        self.grid[0, 3] = self.rightSPICE

    def display_gds(self, gds_file, scale = 3):
        # Generate an SVG image
        top_level_cell = gdstk.read_gds(gds_file).top_level()[0]
        top_level_cell.write_svg('out.svg')

        # Scale the image for displaying
        fig = sg.fromfile('out.svg')
        fig.set_size((str(float(fig.width) * scale), str(float(fig.height) * scale)))
        fig.save('out.svg')

        # Display the image
        IPython.display.display(IPython.display.SVG('out.svg'))

    def display_component(self, component, scale = 3):
        # Save to a GDS file
        with self.hide:
            component.write_gds("out.gds")

        self.display_gds('out.gds', scale)

#with hide:
#  # Generate the sky130 component
#  component_sky130 = nmos(pdk = sky130, fingers=5)
  # Generate the gf180 component
#  component_gf180 = nmos(pdk = gf180, fingers=5)

# Display the components' GDS and SPICE netlists
#with left:
#  print('Skywater 130nm N-MOSFET (fingers = 5)')
#  display_component(component_sky130, scale=2.5)
#with leftSPICE:
#  print('Skywater 130nm SPICE Netlist')
#  print(component_sky130.info['netlist'].generate_netlist())

#with right:
#  print('GF 180nm N-MOSFET (fingers = 5)')
#  display_component(component_gf180, scale=2)
#with rightSPICE:
# print('GF 180nm SPICE Netlist')
#  print(component_gf180.info['netlist'].generate_netlist())