import bpy
from mathutils import Color

from PIL import Image, ImageDraw
import time


def get_material_color(mat):
    nodes = mat.node_tree.nodes
    principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    # Get the slot for 'base color'
    base_color = principled.inputs['Base Color']  # Or principled.inputs[0]
    # Get its default value (not the value from a possible link)
    value = base_color.default_value

    color = Color((value[0], value[1], value[2]))
    print(color)

    return color

# MAIN


start_time = time.time()

# prepare
tex_size = 128
img = Image.new('RGB', (tex_size, tex_size), color='black')
draw = ImageDraw.Draw(img)

me = bpy.context.object.data
uv_layer = me.uv_layers.active.data

mats = me.materials

# cache colors
mat_colors = []

for mat in mats:
    col = get_material_color(mat)
    mat_colors.append((int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

# go through polygons and render them on the texture
for poly in me.polygons:
    print("Polygon index: %d, length: %d" % (poly.index, poly.loop_total))
    print("Loop index: %d" % (poly.material_index))
    col = mat_colors[poly.material_index]
    print("Color: " + str(mat_colors[poly.material_index]))

    uvs = []
    for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
        print("    Vertex: %d" % me.loops[loop_index].vertex_index)
        print("    UV: %r" % uv_layer[loop_index].uv)
        uv = uv_layer[loop_index].uv
        uvs.append((uv.x * tex_size, uv.y * tex_size))

    draw.polygon(uvs, fill=col)

img.show()

print("--- %s seconds ---" % (time.time() - start_time))
