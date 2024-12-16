####
# Compiled Glayout
# Apache License
# Version 2.0, January 2004
# http://www.apache.org/licenses/
# 2024-12-15 20:38:21.158328

from glayout.flow.pdk.mappedpdk import MappedPDK
from gdsfactory import Component
from glayout.flow.pdk.util.comp_utils import move, movex, movey, prec_ref_center, evaluate_bbox, center_to_edge_distance
from glayout.flow.pdk.util.port_utils import remove_ports_with_prefix
from glayout.flow.primitives.fet import nmos
from glayout.flow.primitives.fet import pmos
from glayout.flow.primitives.guardring import tapring
from glayout.flow.primitives.mimcap import mimcap
from glayout.flow.primitives.mimcap import mimcap_array
from glayout.flow.primitives.via_gen import via_stack
from glayout.flow.primitives.via_gen import via_array
from glayout.flow.placement.two_transistor_interdigitized import two_nfet_interdigitized
from glayout.flow.placement.four_transistor_interdigitized import generic_4T_interdigitzed
from glayout.flow.placement.two_transistor_interdigitized import two_pfet_interdigitized
from glayout.flow.blocks.diff_pair import diff_pair_generic
from glayout.flow.routing.smart_route import smart_route
from glayout.flow.routing.L_route import L_route
from glayout.flow.routing.c_route import c_route
from glayout.flow.routing.straight_route import straight_route

def layout_cell(
	pdk: MappedPDK,
	input_width: float, 
	input_length: float, 
	input_multiplier: int, 
	input_fingers: int, 
):
	pdk.activate()
	layout = Component(name="layout")
	maxmetalsep = pdk.util_max_metal_seperation()
	double_maxmetalsep = 2*pdk.util_max_metal_seperation()
	triple_maxmetalsep = 3*pdk.util_max_metal_seperation()
	quadruple_maxmetalsep = 4*pdk.util_max_metal_seperation()
	# placing input_positive centered at the origin
	input_positive = nmos(pdk,**{'width': input_width, 'length': input_length, 'fingers': input_fingers, 'rmult': 1, 'multipliers': input_multiplier, 'with_substrate_tap': False, 'with_tie': True, 'with_dummy': True, 'with_dnwell': False})
	input_positive_ref = prec_ref_center(input_positive)
	layout.add(input_positive_ref)
	layout.add_ports(input_positive_ref.get_ports_list(),prefix="input_positive_")
	# placing input_negative centered at the origin
	input_negative = nmos(pdk,**{'width': input_width, 'length': input_length, 'fingers': input_fingers, 'rmult': 1, 'multipliers': input_multiplier, 'with_substrate_tap': False, 'with_tie': True, 'with_dummy': True, 'with_dnwell': False})
	input_negative_ref = prec_ref_center(input_negative)
	layout.add(input_negative_ref)
	layout.add_ports(input_negative_ref.get_ports_list(),prefix="input_negative_")
	# move input_negative right input_positive
	relativemovcorrection_0 = 1*(maxmetalsep + center_to_edge_distance(input_positive_ref,3) + center_to_edge_distance(input_negative_ref,1))
	movex(input_negative_ref,destination=(relativemovcorrection_0 + input_positive_ref.center[0]))
	remove_ports_with_prefix(layout,"input_negative_")
	layout.add_ports(input_negative_ref.get_ports_list(),prefix="input_negative_")
	layout << smart_route(pdk,layout.ports["input_positive_source_N"],layout.ports["input_negative_source_N"],input_positive_ref,layout,**{})
	return layout
