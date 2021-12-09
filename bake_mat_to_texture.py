# By Nothke

import bpy
from mathutils import Color
from numpy.core.fromnumeric import repeat
import numpy
from PIL import Image, ImageDraw, ImageFilter
import time
bl_info = {
    "name": "Mat2id Baker",
    "description": "Bakes material to id map without Cycles.",
    "author": "Nothke",
    "category": "Object",
    "blender": (2, 80, 0),
    #    "location": "Object > Apply > Unity Rotation Fix",
}


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

    # img = Image.blend(img, img_blurred, 0.5)

    # for y in range(size):
    #     for x in range(size):
    #         if img.getpixel((x,y))[0] < 10:
    #             img.putpixel((x, y), (255,255,255))

    # for i in range(10):
    #     img = img.filter(ImageFilter.MaxFilter(3))

    # img = img.filter(ImageFilter.Kernel((3, 3),
    #     (1, 1, 1,
    #      1, 1, 1,
    #      1, 1, 1), 1, 0))

    if inflate_iterations > 0:
        img_max = img

        for i in range(inflate_iterations):
            img_max = img_max.filter(ImageFilter.MaxFilter(3))

        arr = numpy.array(img)
        arr_max = numpy.array(img_max)

        # Slow! TODO: Convert to numpy array operators
        for y in range(size):
            for x in range(size):
                # if alpha is 0 and inflated's alpha is more than 0
                if arr[x, y, 3] == 0 and arr_max[x, y, 3] > 0:
                    # set pixel to inflated
                    arr[x, y] = arr_max[x, y]
                    # set alpha to max
                    arr[x, y, 3] = 255

        # converted for loop to numpy:
        # comp = numpy.logical_and(arr[:, :, 3] == 0, arr_max[:, :, 3] > 0)
        # arr[:,:] = comp * arr_max #bad?

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
    prop_custom_file_path: bpy.props.StringProperty(
        name="Custom File Path", default="", description="If empty, the path will be .blend_folder/active_object's_name.png")
    prop_tex_size: bpy.props.IntProperty(name="Texture Size", default=512)
    prop_supersampling: bpy.props.IntProperty(
        name="Supersampling", default=0, description="Effectively supersampling-antialiasing. Doubles the size of the drawing texture that will get scaled down to Texture Size at the end.")
    prop_inflate_iterations: bpy.props.IntProperty(
        name="Inflate Iterations", default=3)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        return main(self, context,
                    self.prop_tex_size,
                    supersample=self.prop_supersampling,
                    inflate_iterations=self.prop_inflate_iterations,
                    custom_file_path=self.prop_custom_file_path)

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
