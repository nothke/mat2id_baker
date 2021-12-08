import bpy
from mathutils import Color

from PIL import Image, ImageDraw, ImageFilter
import time

# ---- PROPERTIES ----
tex_size = 256
file_path = "baked_test.png"
supersample = 2


# ---- CODE ----

# static functions:

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


def get_blend_folder():
    if not bpy.data.is_saved:
        raise Exception("Cannot bake as the blend file is not yet saved")

    folder_path = bpy.path.abspath("//")
    if folder_path is None:
        raise Exception("File path is invalid for some reason.")

    return folder_path

# ---- MAIN ----


def main(context):
    print("Running")

    folder_path = get_blend_folder()

    start_time = time.time()

    # prepare
    me = bpy.context.object.data
    uv_layer = me.uv_layers.active.data

    mats = me.materials

    if len(mats) == 0:
        raise Exception("Object has no materials")

    # make image
    size = tex_size
    for i in range(supersample):
        size *= 2

    img = Image.new('RGB', (size, size), color='black')
    draw = ImageDraw.Draw(img)

    selected_objects = []
    for obj in context.selected_objects:
        if obj.type != "MESH":  # Skip non-mesh
            obj.select_set(False)
            continue

    # cache colors
    mat_colors = []

    for mat in mats:
        col = get_material_color(mat)
        mat_colors.append(
            (int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

    # go through polygons and render them on the texture
    for poly in me.polygons:
        #print("Polygon index: %d, length: %d" % (poly.index, poly.loop_total))
        #print("Loop index: %d" % (poly.material_index))
        col = mat_colors[poly.material_index]
        #print("Color: " + str(mat_colors[poly.material_index]))

        uvs = []
        for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
            #print("    Vertex: %d" % me.loops[loop_index].vertex_index)
            #print("    UV: %r" % uv_layer[loop_index].uv)
            uv = uv_layer[loop_index].uv
            uvs.append((uv.x * size, uv.y * size))

        draw.polygon(uvs, fill=col)

    #img_blurred = img.filter(ImageFilter.GaussianBlur(radius=6))
    #img = img_blurred
    #img = Image.blend(img, img_blurred, 0.5)

    img = img.resize((tex_size, tex_size), resample=Image.BICUBIC)

    # img.show()
    img.save(folder_path + file_path, "PNG")

    print("--- Finished baking in %s seconds ---" % (time.time() - start_time))


# ---- BLENDER ----

class NOTHKE_OT_mat2id_baker(bpy.types.Operator):
    """Bakes material colors to id texture without Cycles"""
    bl_idname = "object.mat2id_baker"
    bl_label = "mat2id baker"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}

# ---- REGISTRATION ----


def register():
    bpy.utils.register_class(NOTHKE_OT_mat2id_baker)


def unregister():
    bpy.utils.unregister_class(NOTHKE_OT_mat2id_baker)


if __name__ == "__main__":
    register()

# test call
bpy.ops.object.mat2id_baker()
