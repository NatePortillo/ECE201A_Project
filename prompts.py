import os

STRICT_SYNTAX_INSTRUCT = """
What is Glayout strict syntax
Glayout strictsyntax is a command language for producing analog circuit layout. Glayout strictsyntax allows the designer to place, move, and connect circuit Components without needing to draw them, rather with strictsyntax the designer can describe them in simple words and with simple commands.

Strict Syntax Commands
Strict syntax supports the commands listed below. Note I have left square brackets [] around places where specific command calls should fill in information.

Import Command
Sometimes you want to use Components which are not included in the Glayout runtime. You do this using the import command. The import command automatically searches for the Component path, so you do not need to specify a path. All you need is to specify the Component you want. The general syntax for importing a Component is: import [Component] For example, to import a CrossCoupledInvereters, the user could do the following: import CrossCoupledInverters

Create Parameters Command
You generally want to make the Components as parameterized as possible so that they are highly modular and customizable. To do this you need to create parameters. You can create parameters with the following general command syntax: create a [Type] parameter called [ParameterName] Here are some examples using the create parameter command: create a float parameter called device_width create a int parameter called device_fingers

Place Command
The general syntax for the place command is below. I have left square brackets around names of Components or ComponentRefs or parameters that should be inserted when using the command. When you insert parameters, you can specify them as a comma separated list. place a [Component] called [ComponentRef] with [parameters] An example of using the place command is as follows: place a nmos called m1 with width 1.0, length 2.0, fingers 2, rmult 1, multipliers 3, with_substrate_tap False, with_tie True, with_dummy True, with_dnwell False The parameter list also supports passing existing parameter names instead of values.

Move Command
By default all placed Components are centered at the origin. Obviously, if we place more than one ComponentRef we need to move some of them so that they are not overlapping. To emphasize, if more than one ComponentRef is placed, at least one ComponentRef must be moved to avoid overlapping. To do this, use the move command. The move command allows you to specify relative movements relative to other placed ComponentRefs. The general relative move syntax is as follows: move [ComponentRef we are moving] [relative direction] [relative to ComponentRef] Directions include above, below, right, or left. Here is an example of using relative move (say we have a ComponentRef called m1 and another called m2): move m1 below m2

Route Command
Routes are connections between 2 Ports. There are 4 types of routes: straight_route, c_route, L_route, and smart_route. Unless you are very confident, always use smart_route. Only under special circumstances you can specifcy a different route type, but in almost all cases smart_route is the best option. smart_route can almost always optimally route between two ports. There are also some rules you can use to determine the Port orientations. If you are routing between ComponentRefs which are left or right of each other, then select Ports which are on the adjacent sides. If you are routing between ComponentRefs above or below each other, then select Ports that are both on the East side or both on the West side. The general route syntax is as follows: route between [Port1] and [Port2] using [route_type] For example, if we have a nmos ComponentRef called m1 which is to the west of a pmos ComponentRef called m2, an example route command to connect the sources of both would be as follows: route between m1_source_E and m2_source_W using smart_route Note that the first part of the portname is the ComponentRef name. Also, notice why the E and W ports were chosen. The nmos ComponentRef called m1 is to the left of the pmos ComponentRef called m2, so the sides adjacent to each other are the east side of m1 and west side of m2. If m1 was above m2, then I could have selected both East Ports or both West Ports as follows: route between m1_source_E and m2_source_E using smart_route or route between m1_source_W and m2_source_W using smart_route

StrictSyntax Style Guide
When specifying component parameters always use named arguments. You should always follow this order of commands when creating a Component with strictsyntax: Start by importing any required Components, then create any required parameters, then place all required ComponentRefs with their respective parameters, then move all ComponentRefs to their final positions relative to one another, and lastly route between ComponentRefs. Do not place components overlapping (always move components if more than one is placed)
"""

USER_PROMPT = "Create a simple differential amplifier using two matched nMOS transistors as the input pair."


API_KEY=os.getenv("API_KEY")
API_KEY= "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"
KG_PASSWORD=os.getenv("KG_PASSWORD")
