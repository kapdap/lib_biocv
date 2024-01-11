########################################################################################################################
# IO_RDX - BIOHAZARD CODE VERONICA X BLENDER IMPORT ADDON
#=======================================================================================================================
# 2015, 2019 MORTICIAN (THE_MORTICIAN@HOTMAIL.DE)
########################################################################################################################
import os
import bpy
import imp
import lib_biocv.lib_rdx as lib_rdx

imp.reload(lib_rdx)

def format_id(id):
    return f"{id:03d}"

def import_point(name, data, rdx_collection):
    sub_collection = bpy.data.collections.new(name=name)
    rdx_collection.children.link(sub_collection)
    
    if data.object:
        for i, obj in enumerate(data.object):
            point = bpy.data.objects.new(f'{name}_{format_id(i)}', None)
            point.location = (obj.x, -obj.z, obj.y)
            sub_collection.objects.link(point)

        bpy.context.view_layer.update()

def import_volume(name, data, rdx_collection, color=(0.5, 0.5, 0.5, 1.0)):
    sub_collection = bpy.data.collections.new(name=name)
    rdx_collection.children.link(sub_collection)

    if data.object:
        faces = [(0, 1, 2, 3),
                 (0, 4, 5, 1),
                 (0, 3, 7, 4),
                 (2, 3, 7, 6),
                 (4, 5, 6, 7),
                 (1, 2, 6, 5)]
        
        material_name = f'{name}_MATERIAL' 
        material = bpy.data.materials.get(material_name) or bpy.data.materials.new(material_name)
        material.diffuse_color = color

        for i, obj in enumerate(data.object):
            verts = [(obj.x, -obj.z, obj.y),
                     (obj.x + obj.width, -obj.z, obj.y),
                     (obj.x + obj.width, -obj.z - obj.density, obj.y),
                     (obj.x, -obj.z - obj.density, obj.y),
                     (obj.x, -obj.z, obj.height),
                     (obj.x + obj.width, -obj.z, obj.height),
                     (obj.x + obj.width, -obj.z - obj.density, obj.height),
                     (obj.x, -obj.z - obj.density, obj.height)]
            
            mesh = bpy.data.meshes.new(f'{name}_{format_id(i)}_MESH')
            mesh.from_pydata(verts, [], faces)
            mesh.materials.append(material)
            mesh.update()
            
            volume = bpy.data.objects.new(f'{name}_{format_id(i)}', mesh)
            sub_collection.objects.link(volume)

        bpy.context.view_layer.update()

def import_file(context, filepath):
    print("BIOHAZARD CODE VERONICA X .RDX FILE IMPORT")
    print('IMPORTING FILE: ' + filepath)
    
    tmp_rdx = lib_rdx.rdx_file()
    tmp_rdx = lib_rdx.rdx_file.read(tmp_rdx, filepath)

    rdx_collection = bpy.data.collections.new(name=os.path.splitext(os.path.basename(filepath))[0])
    bpy.context.scene.collection.children.link(rdx_collection)
    
    import_point("ACT", tmp_rdx.actor, rdx_collection)
    import_point("OBJ", tmp_rdx.obj, rdx_collection)
    import_point("ITM", tmp_rdx.item, rdx_collection)
    import_volume("EFF", tmp_rdx.effect, rdx_collection, (1.0, 0.0, 0.0, 1.0))
    import_volume("SCA", tmp_rdx.sca, rdx_collection, (0.5, 0.5, 0.5, 1.0))
    import_volume("AOT", tmp_rdx.aot, rdx_collection, (1.0, 0.5, 0.0, 1.0))
    import_volume("TRG", tmp_rdx.trigger, rdx_collection, (0.0, 0.0, 1.0, 1.0))
    import_point("PLY", tmp_rdx.player, rdx_collection)

    return {'FINISHED'}

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

class rdx_importer(Operator, ImportHelper):
    """Load a RDX file"""
    bl_idname = "recv_tools.rdx_import"  # important since its how bpy.ops.recv_tools.rdx_import is constructed
    bl_label = "Import RDX"

    filename_ext = ".rdx"

    filter_glob = StringProperty(
            default="*.rdx",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return import_file(context, self.filepath)

def menu_func_import(self, context):
    self.layout.operator(rdx_importer.bl_idname, text="RDX (.rdx)")

def register():
    bpy.utils.register_class(rdx_importer)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(rdx_importer)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.recv_tools.rdx_import('INVOKE_DEFAULT')
