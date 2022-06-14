#!$BLENDER_PATH/python/bin python

import pathlib
import re

import bpy
import bpy_types


PBR_IMG_DATA = {
    'Albedo': {
        'colorspace_settings': 'sRGB',
    },
    'Alpha': {
        'colorspace_settings': 'Non-Color',
    },
    'AmbientOcclusion': {
        'colorspace_settings': 'Non-Color',
    },
    'BaseColor': {
        'colorspace_settings': 'sRGB',
    },
    'Diffuse': {
        'colorspace_settings': 'sRGB',
    },
    'Displace': {
        'colorspace_settings': 'Non-Color',
    },
    'Emission': {
        'colorspace_settings': 'sRGB',
    },
    'Glossiness': {
        'colorspace_settings': 'Non-Color',
    },
    'Height': {
        'colorspace_settings': 'Non-Color',
    },
    'Metallic': {
        'colorspace_settings': 'Non-Color',
    },
    'Metalness': {
        'colorspace_settings': 'Non-Color',
    },
    'Normal': {
        'colorspace_settings': 'Non-Color',
    },
    'Roughness': {
        'colorspace_settings': 'Non-Color',
    },
    'Subsurface': {
        'colorspace_settings': 'sRGB',
    },
}


# def mtl_search_replace_tex_image_dir_paths(
#     mesh_objs: list = [],
#     search_for: str = '',
#     replace_with: str = '',
# ):
#     """"""
#     if not mesh_objs:
#         mesh_objs = (obj for obj in bpy.data.objects if obj.type == 'MESH')

#     re_img_data_pattern = re.compile(
#         fr'^.+_(?P<img_data_name>({"|".join(PBR_IMG_DATA.keys())}))\.(?P<ext>\w+)$'
#     )
#     mtl_list = []

#     for mesh_obj in mesh_objs:
#         mesh_data = mesh_obj.data
#         for mtl in mesh_data.materials:
#             if mtl not in mtl_list:
#                 mtl_list.append(mtl)
    
#     tex_imgs = []
            
#     for mtl in mtl_list:

#         for grp in (n for n in mtl.node_tree.nodes if n.type == 'GROUP'):
#             for tex_img in (n for n in grp.node_tree.nodes if n.type == 'TEX_IMAGE'):
#                 tex_imgs.append(tex_img)
        
#         for tex_img in (n for n in mtl.node_tree.nodes if n.type == 'TEX_IMAGE'):
#             tex_imgs.append(tex_img)
            
#     for tex_img in tex_imgs:
    
#         repathed_fp = pathlib.Path(tex_img.image.filepath.replace(search_for, replace_with))
#         re_match = re_img_data_pattern.match(repathed_fp.as_posix())
        
#         if re_match:
            
#             img_suffix = re_match.group('img_data_name')
#             colorspace_settings = PBR_IMG_DATA.get(img_suffix)['colorspace_settings']
            
#             repathed_fp_str = '//' + str(repathed_fp).lstrip('\\')
#             tex_img.image.filepath = repathed_fp_str
#             tex_img.image.colorspace_settings.name = colorspace_settings


def mtl_search_replace_image_dir_paths(
    search_for: str = '',
    replace_with: str = '',
    collection: bpy_types.Collection = None,
):
    """"""

    if collection:
        img_nodes, mtl_list = [], []
        for obj in collection.all_objects:
            if obj.type == 'MESH':
                for mtl in obj.data.materials:
                    if mtl not in mtl_list:
                        for grp in (n for n in mtl.node_tree.nodes if n.type == 'GROUP'):
                            for tex_img in (n for n in grp.node_tree.nodes if n.type == 'TEX_IMAGE'):
                                img_nodes.append(tex_img.image)
                        for tex_img in (n for n in mtl.node_tree.nodes if n.type == 'TEX_IMAGE'):
                            img_nodes.append(tex_img.image)
                    mtl_list.append(mtl)

    else:
        img_nodes = bpy.data.images

    re_img_data_pattern = re.compile(
        fr'^.+_(?P<img_data_name>({"|".join(PBR_IMG_DATA.keys())}))\.(?P<ext>\w+)$'
    )

    for img_node in img_nodes:
    
        repathed_fp = pathlib.Path(img_node.filepath.replace(search_for, replace_with))
        re_match = re_img_data_pattern.match(repathed_fp.as_posix())
        
        if re_match:
            
            img_suffix = re_match.group('img_data_name')
            colorspace_settings = PBR_IMG_DATA.get(img_suffix)['colorspace_settings']
            
            repathed_fp_str = '//' + str(repathed_fp).lstrip('\\')
            img_node.filepath = repathed_fp_str
            img_node.colorspace_settings.name = colorspace_settings


def mtl_set_material_data(
    material_name: str = None,
    mesh_objs: list = [],
):
    """"""
    if material_name and mesh_objs:

        material = bpy.data.materials.get(material_name)
        for mesh_obj in (obj for obj in mesh_objs if obj.type == 'MESH'):
            mesh_obj.active_material = material
