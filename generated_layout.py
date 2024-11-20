####
# Compiled Glayout
# Apache License
# Version 2.0, January 2004
# http://www.apache.org/licenses/
# 2024-11-20 14:10:51.415390

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
	inverter_width: float, 
	inverter_length: float, 
	inverter_fingers: int, 
):
	pdk.activate()
	layout = Component(name="layout")
	maxmetalsep = pdk.util_max_metal_seperation()
	double_maxmetalsep = 2*pdk.util_max_metal_seperation()
	triple_maxmetalsep = 3*pdk.util_max_metal_seperation()
	quadruple_maxmetalsep = 4*pdk.util_max_metal_seperation()
	# placing n1 centered at the origin
	n1 = nmos(pdk,**{'width': inverter_width, 'length': inverter_length, 'fingers': inverter_fingers, 'rmult': 1, 'multipliers': 1, 'with_substrate_tap': False, 'with_tie': True, 'with_dummy': False})
	n1_ref = prec_ref_center(n1)
	layout.add(n1_ref)
	layout.add_ports(n1_ref.get_ports_list(),prefix="n1_")
	# placing n2 centered at the origin
	n2 = nmos(pdk,**{'width': inverter_width, 'length': inverter_length, 'fingers': inverter_fingers, 'rmult': 1, 'multipliers': 1, 'with_substrate_tap': False, 'with_tie': True, 'with_dummy': False})
	n2_ref = prec_ref_center(n2)
	layout.add(n2_ref)
	layout.add_ports(n2_ref.get_ports_list(),prefix="n2_")
	# placing p1 centered at the origin
	p1 = pmos(pdk,**{'width': inverter_width, 'length': inverter_length, 'fingers': inverter_fingers, 'rmult': 1, 'multipliers': 1, 'with_substrate_tap': False, 'with_tie': True, 'with_dummy': False})
	p1_ref = prec_ref_center(p1)
	layout.add(p1_ref)
	layout.add_ports(p1_ref.get_ports_list(),prefix="p1_")
	# placing p2 centered at the origin
	p2 = pmos(pdk,**{'width': inverter_width, 'length': inverter_length, 'fingers': inverter_fingers, 'rmult': 1, 'multipliers': 1, 'with_substrate_tap': False, 'with_tie': True, 'with_dummy': False})
	p2_ref = prec_ref_center(p2)
	layout.add(p2_ref)
	layout.add_ports(p2_ref.get_ports_list(),prefix="p2_")
	# move n2 below n1
	relativemovcorrection_0 = -1*(maxmetalsep + center_to_edge_distance(n1_ref,4) + center_to_edge_distance(n2_ref,2))
	movey(n2_ref,destination=(relativemovcorrection_0 + n1_ref.center[1]))
	remove_ports_with_prefix(layout,"n2_")
	layout.add_ports(n2_ref.get_ports_list(),prefix="n2_")
	# move p2 below p1
	relativemovcorrection_0 = -1*(maxmetalsep + center_to_edge_distance(p1_ref,4) + center_to_edge_distance(p2_ref,2))
	movey(p2_ref,destination=(relativemovcorrection_0 + p1_ref.center[1]))
	remove_ports_with_prefix(layout,"p2_")
	layout.add_ports(p2_ref.get_ports_list(),prefix="p2_")
	return layout
