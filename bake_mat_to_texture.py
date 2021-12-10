# By Nothke

bl_info = {
    "name": "Mat2id Baker",
    "description": "Bakes material to id map without Cycles.",
    "author": "Nothke",
    "category": "Object",
    "blender": (2, 80, 0),
    #    "location": "Object > Apply > Unity Rotation Fix",
}

print("------------ MAT2ID START ------------")

import bpy
import sys
from mathutils import Color
from numpy.core.fromnumeric import repeat
import numpy
from PIL import Image, ImageDraw, ImageFilter
import time
import pathlib
from os.path import dirname, join

# # IF USING CYTHON:
# # WARNING: this is a fixed location, TODO: change it so it finds the package instead
# module_dir = "C:\\Projects\\py\\nothkes_id_baker"
# if not module_dir in sys.path:
#     sys.path.append(module_dir)
# import pyximport
# pyximport.install()
# import texture_dilate


# ---- CODE ----

# static functions:

def get_material_color(mat):
    # TODO: Handle exceptions if material is not good here
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


def main(self, context,
         tex_size=512,
         supersample=0,
         inflate_iterations=3,
         custom_file_path=""):

    print("Running")

    folder_path = get_blend_folder()

    start_time = time.time()

    # make image
    size = tex_size
    for i in range(supersample):
        size *= 2

    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    selected_objects = []
    #print("Selected: " + str(len(selected_objects)))
    for obj in context.selected_objects:
        if obj.type != "MESH":  # Skip non-mesh
            obj.select_set(False)
            continue

        selected_objects.append(obj)

    # validate first if all objects have materials
    for obj in selected_objects:
        mats = obj.data.materials
        if len(mats) == 0:
            self.report(
                {'ERROR'}, "Cannot bake, object %s has no materials" % (obj.name))
            return {"CANCELLED"}

    for obj in selected_objects:
        mesh = obj.data
        mats = mesh.materials
        uv_layer = mesh.uv_layers.active.data

        # Cache material colors
        mat_colors = []

        for mat in mats:
            col = get_material_color(mat)
            mat_colors.append(
                (int(col[0] * 255), int(col[1] * 255), int(col[2] * 255), 255))

        # Render each polygon on the texture
        for poly in obj.data.polygons:
            col = mat_colors[poly.material_index]

            uvs = []
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                uv = uv_layer[loop_index].uv
                uvs.append((uv.x * size, uv.y * size))

            draw.polygon(uvs, fill=col)

    def clamp(n): return max(0, min(n, size))

    arr = numpy.array(img)

    # Slow! TODO: Convert to numpy array operators..?
    if inflate_iterations > 0:
        # without cython:
        for _ in range(inflate_iterations):
            src = arr.copy()

            for y in range(size):
                for x in range(size):
                    bail = False

                    # skip if pixel is opaque
                    if arr[x, y, 3] > 5:
                        continue

                    startx = x - 1 if x > 0 else 0
                    endx = x + 2 if x < size - 1 else size - 1

                    starty = y - 1 if y > 0 else 0
                    endy = y + 2 if y < size - 1 else size - 1

                    for yi in range(starty, endy):
                        for xi in range(startx, endx):
                            # skip if center pixel
                            if xi == x and yi == y:
                                continue

                            # when an opaque pixel is encountered, color this pixel the same
                            if src[xi, yi, 3] > 5:
                                arr[x, y] = src[xi, yi]
                                bail = True
                                continue

                        if bail:
                            continue

                    if bail:
                        continue

        # IF USING CYTHON:
        # arr = texture_dilate.process(arr, size, inflate_iterations)

        arr[:, :, 3] = 255

        img = Image.fromarray(arr)
    else:
        # convert RGBA to RGB with PIL
        img.load()
        img_rgb = Image.new("RGB", img.size, (0, 0, 0))
        img_rgb.paste(img, mask=img.split()[3])
        img = img_rgb

    img = img.resize((tex_size, tex_size), resample=Image.BICUBIC)

    # img.show()
    file_path = ""
    if custom_file_path:
        file_path = custom_file_path
    else:
        file_path = folder_path + context.active_object.name + ".png"

    img.save(file_path, "PNG")

    self.report({'INFO'}, "Finished baking id texture to %s in %8.3f seconds" %
                (file_path, time.time() - start_time))

    return {'FINISHED'}

# ---- BLENDER ----


class NOTHKE_OT_mat2id_baker(bpy.types.Operator):
    # Description
    """Bakes material colors to id texture without Cycles"""
    bl_idname = "object.mat2id_baker"
    bl_label = "mat2id baker"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties
    custom_file_path: bpy.props.StringProperty(
        name="Custom File Path", default="", description="If empty, the path will be .blend_folder/active_object's_name.png")
    tex_size: bpy.props.IntProperty(name="Texture Size", default=512)
    supersampling: bpy.props.IntProperty(
        name="Supersampling", default=0, description="Effectively supersampling-antialiasing. Doubles the size of the drawing texture that will get scaled down to Texture Size at the end.")
    inflate_iterations: bpy.props.IntProperty(
        name="Inflate Iterations", default=1)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        return main(self, context,
                    self.tex_size,
                    supersample=self.supersampling,
                    inflate_iterations=self.inflate_iterations,
                    custom_file_path=self.custom_file_path)

# ---- REGISTRATION ----


def menu_draw(self, context):
    layout = self.layout
    layout.operator("object.mat2id_baker", text="Mat2id Baker")


def register():
    bpy.utils.register_class(NOTHKE_OT_mat2id_baker)
    bpy.types.VIEW3D_MT_object_apply.append(menu_draw)


def unregister():
    bpy.utils.unregister_class(NOTHKE_OT_mat2id_baker)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_draw)


if __name__ == "__main__":
    register()

# test call
# bpy.ops.object.mat2id_baker()
