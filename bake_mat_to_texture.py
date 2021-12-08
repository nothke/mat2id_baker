import bpy
from mathutils import Color

me = bpy.context.object.data
uv_layer = me.uv_layers.active.data

mats = me.materials
print(mats[0])

# cache colors
mat_colors = []

def get_material_color(mat):
    nodes = mat.node_tree.nodes
    principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    # Get the slot for 'base color'
    base_color = principled.inputs['Base Color']  # Or principled.inputs[0]
    # Get its default value (not the value from a possible link)
    value = base_color.default_value
    
    color = Color((value[0], value[1], value[2]))
    print(color)
    mat_colors.append(color)

for mat in mats:
    col = get_material_color(mat)
    mat_colors.append(col)

for poly in me.polygons:
    print("Polygon index: %d, length: %d" % (poly.index, poly.loop_total))
    print("Loop index: %d" % (poly.material_index))
    print("Color: " + str(mat_colors[poly.material_index]))

    # range is used here to show how the polygons reference loops,
    # for convenience 'poly.loop_indices' can be used instead.
    for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
        print("    Vertex: %d" % me.loops[loop_index].vertex_index)
        print("    UV: %r" % uv_layer[loop_index].uv)
